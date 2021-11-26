var express = require('express');
const multer = require('multer');
var router = express.Router();

const upload = multer();

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
  
    filename: (req, file, cb) => {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname));
    }
});

router.post('/upload', (req, res, next) => {

    // console.log(req.files)

    res.status(200).json({ 'success': true });
});

module.exports = router;
