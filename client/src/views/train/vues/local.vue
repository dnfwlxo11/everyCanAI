<template>
    <div id='local'>
        <div ref="container">
            <div class="row align-items-center mb-2">
                <div class="col-md-2 text-left">
                    <button class="btn btn-primary mb-2" @click="uploadImage" :disabled='!isDisabled'>사진 업로드</button>
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
                    <button class="btn btn-danger mb-2" @click="trainImage" :disabled='isDisabled'>학습 시작</button>
                </div>
            </div>
            <div class="mb-3">
                <div class="row h-100">
                    <div class="col-md-10">
                        <div class="card h-100" ref='files'>
                            <div class="card-header pb-2">
                                <div class="row align-items-center">
                                    <div class="col-2 text-left" @click="moveLeftClass">
                                        <i v-if="currIdx" class="mdi mdi-arrow-left" style="font-size: 16px;"></i>
                                    </div>
                                    <div class="col-8">
                                        <input class="text-center p-0 m-0 card-title" type="text"
                                            v-model="classes[currIdx]" />
                                        <i v-if="isDisabledClass" class="mdi mdi-clipboard-edit-outline ml-3"
                                            style="font-size: 16px;" @click="editClassName()"></i>
                                    </div>
                                    <div class="col-2 text-right">
                                        <i v-if="currIdx==classes.length-1" class="mdi mdi-folder-multiple-plus-outline"
                                            style="font-size: 16px;" @click="addClass()"></i>
                                        <i v-else class="mdi mdi-arrow-right" @click="moveRightClass()"
                                            style="font-size: 16px;"></i>
                                        <i class="mdi mdi-delete ml-3" style="font-size: 16px;color: grey;"
                                            @click="deleteClass(currIdx)"></i>
                                    </div>
                                </div>
                            </div>
                            <div class="card-body p-0 d-flex align-items-center justify-content-center align-items-center"
                                type="fileUpload" @dragenter="onDragenter" @dragover="onDragover"
                                @dragleave="onDragleave" @drop="onDrop" @click="onClick">
                                <div v-if="!fileList[currIdx].length"
                                    class="d-flex align-items-center justify-content-center align-items-center"
                                    :class="isDragged ? 'dragged' : ''" style="height: 500px">
                                    <strong style="width: 100%">Drag & Drop Files</strong>
                                </div>
                                <div v-else class="w-100" style="max-height: 500px; overflow-y:auto; overflow-x:hidden;">                                    
                                    <div class="row m-0">
                                        <div class="col-md-3 p-1" v-for="(file, index) in fileList[currIdx]" :key="index">
                                            <div class="card">
                                                <div style="position: relative;">
                                                    <img class="w-100"
                                                        height="100px"
                                                        :src="imageResize(file).src" @click.stop="">
                                                    <div style="position: absolute;top: 0; right:0"
                                                        @click.stop="handleRemove(index)">
                                                        <a href="javascript:;"><i class="mdi mdi-delete"></i></a>
                                                    </div>
                                                </div>
                                                <div>
                                                    {{ file.name }}
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3 p-1">
                                            <div class="card">
                                                <div style="position: relative;">
                                                    <i class="mdi mdi-plus w-100" style="font-size: 65px"></i>
                                                </div>
                                                <div>
                                                    파일 추가하기
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <input style="display: none;" type="file" ref="fileInput" @change="onFileChange" multiple>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="card">
                            <div class="card-header pb-2 card-title">
                                클래스 목록
                            </div>
                            <div class="card-body local">
                                <ul>
                                    <li class="mb-2 text-left" @click="currIdx=idx" v-for="(item, idx) in classes"
                                        :key="idx">
                                        {{item}} ({{fileList[idx].length ? fileList[idx].length : 0}})
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <progress-modal v-if="isProgress" msg="작업을 처리 중입니다." />
        <alert-modal v-if="error" msg="클래스가 2개이상, 각 사진이 30장 이상인지 확인해주세요." @on-close="error=false"
            @on-confirm="error=false" />
    </div>
</template>

<script>
    import loadImage from 'blueimp-load-image'
    import axios from 'axios'

    export default {
        name: 'Local',

        data() {
            return {
                webCam: null,
                fileList: [
                    []
                ],
                cardWidth: 0,
                containerHeight: 0,
                isDragged: false,
                classes: ['Class 1'],
                currIdx: 0,
                createNum: 1,
                imagePath: '',
                isDisabled: true,
                isDisabledClass: true,
                isProgress: false,
                error: false
            }
        },

        mounted() {
            this.init()
        },

        methods: {
            init() {
                this.getCardWidth()
            },

            getCardWidth() {
                this.cardWidth = this.$refs.files.clientWidth
                this.containerHeight = this.$refs.container.clientHeight
            },

            onClick() {
                this.$refs.fileInput.click()
            },

            onDragenter(e) {
                this.isDragged = true
            },

            onDragleave(e) {
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
                if (this.currIdx > 0) this.currIdx -= 1
            },

            moveRightClass() {
                if (this.currIdx < this.classes.length - 1) this.currIdx += 1
            },

            async addFiles(files) {
                let tmpArr = []

                for (let i = 0; i < files.length; i++) {
                    const src = await this.readFiles(files[i])
                    files[i].src = src
                    tmpArr.push(files[i])
                }

                this.$set(this.fileList, this.currIdx, this.fileList[this.currIdx].concat(tmpArr))
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
                this.$refs.fileInput.value = ''
                this.fileList[this.currIdx].splice(index, 1)
            },

            deleteClass(index) {
                if (this.classes.length > 1) {
                    this.moveLeftClass();
                    this.$delete(this.classes, index)
                    this.$delete(this.fileList, index)
                }
            },

            addClass() {
                this.classes.push(`Class ${this.createNum + 1}`)

                if (this.classes.length != 1) this.fileList.push([])
                this.createNum += 1
                this.moveRightClass()
            },

            editClassName() {
                this.isDisabledClass = false
            },

            convertFiles() {
                let result = {}

                // 클래스명도 함께
                result['classes'] = this.classes

                // 첨부 파일 정리
                this.fileList.forEach((item, idx) => {
                    result[this.classes[idx]] = item
                })

                return result
            },

            // convertFiles() {
            //     let formData = new FormData()

            //     this.classes.forEach((value, idx) => {
            //         this.fileList[idx].forEach((item, idx) => {
            //             formData.append(value, item)
            //         })
            //     })

            //     return formData
            // },

            uploadImageCheck() {
                let canTrain = true

                // 클래스가 2개 미만이라면 false
                if (this.classes.length < 2) {
                    this.error = true
                    canTrain = false
                }

                this.fileList.forEach(item => {
                    // 클래스 중 하나라도 30장 이하라면 false
                    if (item.length < 30) {
                        this.error = true
                        canTrain = false
                    }
                })

                return canTrain
            },

            imageResize(file) {
                let newFile = loadImage(file, (img) => {
                    return img
                }, {
                    maxWidth: 224,
                    maxHeight: 224
                })
                return newFile
            },

            async uploadImage() {
                if (!this.uploadImageCheck()) return false

                var uploadFiles = this.convertFiles()

                this.isProgress = true

                let res = await axios.post('/node/image/upload', uploadFiles)

                if (res['data']['success']) {
                    this.isDisabled = false
                    this.isProgress = false
                    this.imagePath = res['data']['path']
                } else {
                    this.isProgress = false
                    this.$router.push('/models')
                }
            },

            async trainImage() {
                let res = await axios.post('/node/models/train', {
                    'proj': this.imagePath
                })

                this.isProgress = true

                if (res['data']['success']) {
                    this.isDisabled = false
                    this.$router.push('/models')
                } else {
                    isDisabled
                    this.isDisabled = true
                    return false
                }

                this.isDisabled = false
            },
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
        font-size: 16px;
    }

    .mdi-home-outline {
        font-size: 24px;
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

    ul {
        list-style: none;
        padding-left: 0px;
    }

    .card-title {
        padding-top: 15px;
        padding-bottom: 15px;
    }
</style>