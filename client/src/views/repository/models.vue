<template>
    <div id="models">
        <div class="container pt-3 pb-5 mt-5 mb-5 h-100">
            <div class="row">
                <div class="col mb-3"><div><i class="mdi mdi-home-outline" @click="$router.push({path: '/'})"></i></div>홈</div>
            </div>
            <div class="row d-flex justify-content-center align-items-center">
                <table class="h-100 w-100" border="1">
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
                                학습 중
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    data() {
        return {
            models: []
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
            let res = await axios.get('/api/models')
            this.models = res['data']['models']
        },

        async downloadModel(fileName) {
            let res = await axios.post('/api/download', {'fileName': fileName})

            const url = window.URL.createObjectURL(new Blob([res.data]))
            const link = document.createElement('a')
            link.href = url
            console.log(url)
            link.setAttribute('download', 'output.zip')
            link.click()
        },

        async deleteModel(fileName) {
            console.log(fileName + ' 삭제')
        }
    }
}
</script>

<style>
    html, body {
        height: 100%;
    }

    ul {
        list-style: none;
    }

    td {
        height: 50px;
    }
</style>