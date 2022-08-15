const path = require('path');

module.exports = {
    outputDir: path.resolve(__dirname, '../app_server/public'),
    css: {
        loaderOptions: {
            sass: {
                prependData: `     
                @import "@/assets/scss/_modal.scss";
                `
            }        
        }
    },
    // 개발 서버 설정
    devServer: {
        // 프록시 설정
        proxy: {
            // 프록시 요청을 보낼 api의 시작 부분
            '/woo': {
                // 프록시 요청을 보낼 서버의 주소
                target: 'http://192.168.0.93:16007'
            },
            '/node': {
                // 프록시 요청을 보낼 서버의 주소
                target: 'http://localhost:3000/'
            },
            '/api': {
                // 프록시 요청을 보낼 서버의 주소
                // target: 'http://192.168.0.93:16007'
                target: 'http://localhost:16005'
            },
            
        }
    }
}