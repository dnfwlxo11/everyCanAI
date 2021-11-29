const express = require('express');
const multer = require('multer');
const fs = require('fs');
const router = express.Router();
const path = require('path');

const upload = multer();

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
  
    filename: (req, file, cb) => {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname));
    }
});

router.get('/images/:projId', (req, res, next) => {
    
});

router.post('/upload', (req, res, next) => {
    try {
        let className = req.body['classes'];
        let images = req.body;
        let time = (new Date).getTime();
        let savePath = path.join(__dirname, '..', 'uploads', time.toString());

        if (!fs.existsSync(savePath)) fs.mkdirSync(savePath);

        className.forEach((_class, idx) => {
            let tmpPath = path.join(savePath, _class.toString());

            if (!fs.existsSync(tmpPath)) {
                fs.mkdirSync(tmpPath);
                images[_class].forEach((item, idx2) => {
                    fs.writeFileSync(path.join(tmpPath, `${_class}_${idx2+1}.jpg`), item['src'].split(',')[1], { encoding: 'base64' });
                })
            }
        });

        res.status(200).json({ 'success': true, 'path': path.join('..', 'uploads', time.toString()) });
    } catch(e) {
        console.log(e);
        res.status(200).json({ 'success': false, e });
    }
});

module.exports = router;
