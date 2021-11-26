var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function (req, res, next) {
    console.log('hi');

    let sendData = {}
    sendData['models'] = [{
        'name': '모델1',
        'progress': '완료'
    }]

    res.status(200).send(sendData);
});

module.exports = router;