const express = require('express');
const axios = require('axios');
const router = express.Router();

const api = axios.create({
    baseURL: 'http://localhost:5000',
    timeout: 1000
});

/* GET home page. */
router.get('/', async (req, res, next) => {
    let models = await api({
        method: 'GET',
        url: '/api/models'
    });

    res.status(200).send(models['data']);
});

router.post('/train', (req, res, next) => {
    console.log(req.body)

    // let models = await api({
    //     method: 'GET',
    //     url: '/api/models'
    // });
});

module.exports = router;