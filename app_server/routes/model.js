const express = require('express');
const http = require('http');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const router = express.Router();

const api = axios.create({
    baseURL: 'http://localhost:16005',
    timeout: 60000
});

/* GET home page. */
router.get('/', async (req, res, next) => {
    let models = await api({
        method: 'GET',
        url: '/api/models'
    });

    console.log(models)

    res.status(200).json(models['data']);
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
    
        console.log(trainResult);

        res.status(200).json({ 'success': true });
    } catch (e) {
        console.log(e)
        res.status(200).json({ 'success': false });
    }
});

router.post('/download/:proj', (req, res, next) => {
    console.log(req.params.proj);

    http.get({ path: `/api/download/${req.params.proj}`, hostname: 'localhost', port: 16005 }, (resp) => {
        // res.setHeader('content-disposition', resp.headers['content-disposition']);
        // res.setHeader('Content-Type', resp.headers['Content-Type']);
        resp.pipe(res);
    });
});

module.exports = router;