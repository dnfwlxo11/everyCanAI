var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
const cors = require("cors");

const whitelist = ["http://localhost:8080/"];
const corsOptions = {
  origin: '*'
};

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(logger('dev'));
app.use(express.json({limit: '1024mb'})); 
app.use(express.urlencoded({limit: '1024mb', extended: false}));
app.use(cookieParser());

app.use(express.static(path.join(__dirname, 'public/dist')));
app.use('/images', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.join(__dirname, 'inference')));
app.use(cors()); // 옵션을 추가한 CORS 미들웨어 추가

app.use('/node/image', require('./routes/image'));
app.use('/node/models', require('./routes/model'));
app.use('/node', require('./routes/index'));

// catch 404 and forward to error handler
app.use((req, res, next) => {
  next(createError(404));
});

// error handler
// app.use(function(err, req, res, next) {
//   // set locals, only providing error in development
//   res.locals.message = err.message;
//   res.locals.error = req.app.get('env') === 'development' ? err : {};

//   // render the error page
//   res.status(err.status || 500);
//   res.render('error');
// });

module.exports = app;
