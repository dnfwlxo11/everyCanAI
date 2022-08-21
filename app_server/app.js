const createError = require('http-errors');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const cors = require("cors");
const history = require('connect-history-api-fallback');
require('dotenv').config();

const app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(logger('dev'));
app.use(express.json({limit: '1024mb'})); 
app.use(express.urlencoded({limit: '1024mb', extended: false}));
app.use(cookieParser());

app.use(history());
app.use('/images', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.static(path.join(__dirname, 'inference')));
app.use(cors()); // 옵션을 추가한 CORS 미들웨어 추가

app.use('/node/image', require('./routes/image'));
app.use('/node/models', require('./routes/model'));

// catch 404 and forward to error handler
app.use((req, res, next) => {
  next(createError(404))
})

app.use((err, req, res, next) => {
  const msg = []
  msg.push('\n======================= ERROR =======================')
  msg.push(`Tracing: ${err.stack}`)
  msg.push(`Message: ${err.toString()}`)
  msg.push('======================= ERROR =======================\n')
  console.error(msg.join('\n'))
  res.status(err.status || 500).end()  
})

const server = app.listen(process.env.SERVER_PORT || 80, ()=>{
  const host = server.address().address
  const port = server.address().port
  console.info(`App Listening at http://${host}:${port}`)
})

module.exports = app;
