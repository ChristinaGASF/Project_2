const portNum= 8000;
const NOT_FOUND_ERR= 404, FORBIDDEN_ERR=403, OK=200, INTERNAL_ERR=500;
//const SALT_WORK_FACTOR = 10;
const express= require('express');
const app= express();
const bodyParser= require('body-parser');
//const cookieParser= require('cookie-parser');
//const bcrypt= require('bcrypt');
//const db= require('./models');
//const ctrl = require('./controllers');

app.use(express.json());
app.use(express.static(__dirname+'/public'));
app.use(bodyParser.urlencoded({ extended: true }));



app.get('/', (req,res)=> {
    res.sendFile(__dirname+'/views/index.html');
});




app.listen(process.env.PORT || portNum);