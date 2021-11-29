<template>
    <div id="models">
        <div class="container pt-3 pb-5 mt-5 mb-5 h-100">
            <div class="row">
                <div class="col mb-3"><div><i class="mdi mdi-home-outline" @click="$router.push({path: '/'})"></i></div>홈</div>
            </div>
            <div class="row d-flex justify-content-center align-items-center">
                <table v-if="!isProgress" class="h-100 w-100" border="1">
                    <th>번호</th>
                    <th>프로젝트 명</th>
                    <th>학습 완료 여부</th>
                    <th>관리</th>
                    <tr v-for="(item, idx) of models" :key="idx">
                        <td>
                            {{idx + 1}}
                        </td>
                        <td>
                            {{item['name']}}
                        </td>
                        <td>
                            {{item['progress']}}
                        </td>
                        <td v-if="item['progress']=='학습 완료'">
                            <button class="btn btn-primary mr-3" @click="downloadModel(item['name'])">다운로드</button>
                            <button class="btn btn-danger" @click="deleteModel(item['name'])">삭제</button>
                        </td>
                        <td v-else>
                            <div>
                                {{item['progress']}}
                            </div>
                        </td>
                    </tr>
                </table>
                <div v-else>
                    <i class="mdi mdi-loading mdi-spin mr-2"></i>
                    <span>데이터 로딩 중입니다.</span>
                </div>
            </div>
            <div class="row d-flex justify-content-center align-items-center">
                
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    data() {
        return {
            models: [],
            isProgress: false,
        }
    },

    mounted() {
        this.init()
    },

    methods: {
        init() {
            this.loadModels()
        },

        async loadModels() {
            this.isProgress = true
            let res = await axios.get('/node/models')
            console.log(res)
            this.models = res['data']['models']
            this.isProgress = false
        },

        async downloadModel(fileName) {
            let res = await axios.post(`/node/download/${fileName}`, {}, {
                responseType: 'arraybuffer'
            })

            const url = URL.createObjectURL(new Blob([res.data], {type: 'application/zip'}))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', 'output.zip')
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)
        },

        async deleteModel(fileName) {
            this.isProgress = true

            let res = await axios.post(`/node/delete/${fileName}`)

            if (res.data['success']) {
                this.isProgress = false
                console.log('삭제 성공')
            } else {
                this.isProgress = false
                console.log('삭제 실패')
            }
            
        }
    }
}
</script>

<style>
    ul {
        list-style: none;
    }

    td {
        height: 50px;
    }
</style>