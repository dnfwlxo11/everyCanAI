const express = require('express');
const http = require('http');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const router = express.Router();

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'inference/');
    },
  
    filename: (req, file, cb) => {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname));
    }
});

const inferenece = multer();

const api = axios.create({
    baseURL: 'http://192.168.0.106:16005',
    timeout: 60000
});

router.get('/', async (req, res, next) => {
    try {
        let models = await api({
            method: 'GET',
            url: '/api/models'
        });
    
        res.status(200).json(models['data']);
    } catch (e) {
        res.status(200).json({ 'success': false });
    }
    
});

router.post('/train', async (req, res, next) => {
    let basePath = path.join(__dirname, '..', 'uploads', req.body['proj']);

    let images = {};
    let classes = fs.readdirSync(basePath);
    
    classes.forEach((_class, idx) => {
        images[`${_class}`] = []
        fs.readdirSync(path.join(basePath, _class)).forEach((image, idx2) => {
            images[`${_class}`].push(image);
        })
    });

    let sendData = {
        'proj': req.body['proj'],
        'classes': classes,
        'images': images
    };

    try {
        let trainResult = await api({
            method: 'POST',
            data: sendData,
            url: '/api/train'
        });

        res.status(200).json({ 'success': trainResult['data']['success'] });
    } catch (e) {
        res.status(200).json({ 'success': false });
    }
});

router.post('/download/:proj', (req, res, next) => {
    // api({
    //     method: 'GET',
    //     url: `/api/download/${req.params.proj}`
    // }).then((response) => {
    //     response.pipe(res);
    // });

    http.get({ path: `/api/download/${req.params.proj}`, hostname: 'localhost', port: 16005 }, (resp) => {
        // res.setHeader('content-disposition', resp.headers['content-disposition']);
        // res.setHeader('Content-Type', resp.headers['Content-Type']);
        resp.pipe(res);
    });
});

router.post('/delete/:proj', async (req, res, next) => {
    try {
        let deleteResult = await api({
            method: 'POST',
            url: `/api/delete/${req.params.proj}`
        });
    
        res.status(200).json({ 'success': deleteResult['data']['success'] });
    } catch (e) {
        res.status(200).json({ 'success': false });
    }
});

router.post('/inference', inferenece.single('files'), async (req, res, next) => {
    try {
        let imageTobase64 = req.file['buffer'].toString('base64');
        let inferenceResult = await api({
            method: 'POST',
            url: '/api/inference',
            headers: { 'Content-Type': 'application/json' },
            data: { 
                'file': imageTobase64,
                'model': req.body['model']
            }
        });

        res.status(200).json({ 'success': inferenceResult['data']['success'], 'predict': inferenceResult['data']['predict'] });
    } catch (e) {
        res.status(200).json({ 'success': false });
    }
});

module.exports = router;