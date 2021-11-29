const express = require('express');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const router = express.Router();

const api = axios.create({
    baseURL: 'http://localhost:16005',
    timeout: 1000
});

/* GET home page. */
router.get('/', async (req, res, next) => {
    let models = await api({
        method: 'GET',
        url: '/api/models'
    });

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

    console.log(sendData);

    let trainResult = await api({
        method: 'POST',
        data: sendData,
        url: '/api/train'
    });

    console.log(trainResult['data']);

    res.status(200).json({ 'success': true });
});

module.exports = router;