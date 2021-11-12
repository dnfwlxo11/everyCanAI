<template>
    <div id='local'>
        <div class="container pt-3 pb-5 mt-5 mb-5 vh-100" ref="container">
            <div>
                <div class="row align-items-center">
                    <div class="col-md-2 text-left">
                        <button class="btn btn-primary" @click="uploadImage">사진 업로드</button>
                    </div>
                    <div class="col-md-8">
                        <div>
                            <i class="mdi mdi-home-outline" @click="$router.push({path: '/'})"></i>
                        </div>
                        <div>
                            <strong>홈</strong>
                        </div>
                    </div>
                    <div class="col-md-2 text-right">
                        <button class="btn btn-danger"  @click="trainImage" :disabled='isDisabled'>학습 시작</button>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="row">
                        <div class="col-10">
                            <div class="card" ref='files'>
                                <div class="card-header pb-2">
                                    <div class="row align-items-center">
                                        <div class="col-2 text-left" @click="moveLeftClass">
                                            <i class="mdi mdi-arrow-left"></i>
                                        </div>
                                        <div class="col-8">
                                            <input class="text-center p-0" type="text" v-model="classes[currIdx]" :disabled='isDisabledClass' />
                                            <i v-if="isDisabledClass" class="mdi mdi-clipboard-edit-outline" @click="editClassName()"></i>
                                            <i v-else class="mdi mdi-check" @click="isDisabledClass=true" @blur="isDisabledClass=true"></i>
                                        </div>
                                        <div class="col-2 text-right">
                                            <i v-if="currIdx==classes.length-1" class="mdi mdi-folder-multiple-plus-outline mr-3" @click="addClass();moveRightClass()"></i>
                                            <i v-else class="mdi mdi-arrow-right" @click="moveRightClass()"></i>
                                            <i class="mdi mdi-delete" @click="deleteClass(currIdx)"></i>
                                        </div>
                                    </div>
                                </div>
                                <div class="upload-div" type="fileUpload" @dragenter="onDragenter" @dragover="onDragover"
                                    @dragleave="onDragleave" @drop="onDrop" @click="onClick">
                                    <div v-if="!fileList[currIdx].length" class="file-upload align-items-center" :class="isDragged ? 'dragged' : ''" style="height: 500px">
                                        <strong>Drag & Drop Files</strong>
                                    </div>
                                </div>
                                <input style="display: none;" type="file" ref="fileInput" @change="onFileChange" multiple>
                                <div v-for="(file, index) in fileList[currIdx]" :key="index">
                                    <div style="float: left; padding: 10px">
                                        <div style="position: relative;">
                                            <img class="upload-image" :src="file.src" :width='parseInt(cardWidth / 5) - 25'
                                                :height='parseInt((cardWidth / 5) * 0.56)'>
                                            <div style="position: absolute;top: 0; right:0" @click="handleRemove(index)">
                                                <i class="mdi mdi-delete"></i>
                                            </div>
                                        </div>
                                        <div style="float: left;">
                                            {{ file.name }}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-2">
                            <div class="card">
                                <div class="card-header pb-2">
                                    클래스 목록
                                </div>
                                <div class="card-body local">
                                    <ul>
                                        <li class="mb-2 text-left" @click="currIdx=idx" v-for="(item, idx) in classes" :key="idx">
                                            {{item}} ({{!fileList[idx].length ? fileList[idx].length : 0}})
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <div class="mb-3">
                            <div class="card">
                                <div class="card-header text-left pb-0">
                                    <h5><strong>모델 정보</strong><small> (BaseModel. resnet50)</small></h5>
                                </div>
                                <div v-if="modelInfo==null" class="card-body">모델 정보를 불러오는 중입니다.</div>
                                <div v-else class="card-body">{{modelInfo}}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'Local',

    data() {
        return {
            mode: 'local',
            webCam: null,
            fileList: [[]],
            cardWidth: 0,
            containerHeight: 0,
            isDragged: false,
            modelInfo: null,
            classes: ['Class 1'],
            currIdx: 0,
            createNum: 1,
            isDisabled: true,
            isDisabledClass: true,
        }
    },

    mounted() {
        this.init()
    },

    methods: {
        init() {
            this.getCardWidth()
            this.getModel()
        },

        getCardWidth() {
            this.cardWidth = this.$refs.files.clientWidth
            this.containerHeight = this.$refs.container.clientHeight
        },

        onClick() {
            this.$refs.fileInput.click()
        },

        onDragenter(e) {
            // class 넣기
            this.isDragged = true
        },

        onDragleave(e) {
            // class 삭제
            this.isDragged = false
        },

        onDragover(e) {
            e.preventDefault()
        },

        onDrop(e) {
            e.preventDefault()
            this.isDragged = false
            const files = e.dataTransfer.files
            this.addFiles(files)
        },

        onFileChange(e) {
            const files = e.target.files
            this.addFiles(files)
        },

        moveLeftClass() {
            if (this.currIdx > 0) this.currIdx-=1
        },

        moveRightClass() {
            if (this.currIdx < this.classes.length) this.currIdx+=1
        },

        async addFiles(files) {
            let tmpArr = []

            for (let i = 0; i < files.length; i++) {
                const src = await this.readFiles(files[i])
                files[i].src = src
                tmpArr.push(files[i])
            }

            this.fileList[this.currIdx].concat(tmpArr)
        },

        async readFiles(files) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader()
                reader.onload = async (e) => {
                    resolve(e.target.result)
                }
                reader.readAsDataURL(files)
            })
        },

        handleRemove(index) {
            this.fileList[this.currIdx].splice(index, 1)
        },

        deleteClass(index) {
            if (index) {
                this.moveLeftClass();
                this.classes.splice(index, 1)
                this.fileList.splice(index, 1)
            }
        },

        addClass() {
            this.classes.push(`Class ${this.createNum + 1}`)
            this.fileList.push([])
            this.createNum += 1
        },

        editClassName() {
            this.isDisabledClass = false
        },

        convertFiles() {
            let result = {}

            this.fileList.forEach((item, idx) => {
                result[this.classes[idx]] = item
            })

            return result
        },

        async getModel() {
            let res = await axios.get('/api/information')
            this.modelInfo = res.data.info
        },

        async uploadImage() {
            console.log(this.convertFiles())


            let res = await axios.post('/api/upload', this.fileList)

            

            console.log('이미지 업로드')
            this.isDisabled = false
        },

        async trainImage() {
            console.log('학습 시작')
        }
    }
}
</script>

<style>
html,
    body {
        height: 100%;
        margin: 0;
    }    

    .mdi {
        font-size: 24px;
    }

    .mdi-home-outline {
        font-size: 36px;
    }

    .dragged {
        border: 1px dashed powderblue;
        opacity: .6;
    }

    .upload-image {
        border: solid grey 1px;
    }

    .local {
        overflow: scroll;
        overflow-x: hidden;
        max-height: 500px;
        min-height: 500px;
    }

    .after {
        overflow: scroll;
    }
    
    ul {
        list-style: none;
        padding-left: 0px;
    }
</style>