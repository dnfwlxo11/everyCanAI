<template>
    <div id="inference">
        <div class="container pt-5 pb-5 mt-5 mb-5">
            <div class="row mb-3">
                <div class="col mb-3">
                    <div><i class="mdi mdi-home-outline" @click="$router.push({path: '/'})"></i></div>홈
                </div>
                <!-- <button class="btn btn-primary" @click="printImage">출력</button> -->
            </div>
            <div class="row mb-3 align-items-center">
                <div class="col-md-5">
                    <div class="card">
                        <div class="card-header">
                            <strong>분류하고 싶은 사진</strong> <small>(Model. InceptionV3)</small>
                            <i v-if="file!=null" class="mdi mdi-refresh ml-3" style="font-size: 18px;color: black;"
                                @click="deleteImage"></i>
                        </div>
                        <div class="card-body" style="min-height: 400px">
                            <div class="upload-div" type="fileUpload" @dragenter="onDragenter" @dragover="onDragover"
                                @dragleave="onDragleave" @drop="onDrop" @click="onClick">
                                <div v-if="file==null"
                                    class="h-100 d-flex align-items-center justify-content-center file-upload align-items-center">
                                    <strong>Drag & Drop Files</strong>
                                </div>
                                <div v-else>
                                    <img class="preview" :src='thumbnail' height="100%" width="100%">
                                    <div class="mt-3"><strong>{{file.name}}</strong></div>
                                </div>
                            </div>
                        </div>
                        <input style="display: none;" type="file" ref="fileInput" @change="onFileChange">
                    </div>
                </div>
                <div class="col-md-2">
                    <div>
                        <i class="mdi mdi-arrow-right-bold-outline" style="font-size:48px;"></i>
                    </div>
                    <div>
                        <button class="btn btn-outline-primary" @click="inference">분류하기</button>
                    </div>
                </div>
                <div class="col-md-5">
                    <div class="card">
                        <div class="card-header">
                            <strong>분류 결과</strong>
                        </div>
                        <div class="card-body" style="min-height: 400px">
                            <div v-if="isComplate">
                                <img class="preview" :src='thumbnail' height="100%" width="100%">
                                <div class="mt-3"><strong>{{predict}}</strong></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="input-group mb-3">
                    <select class="custom-select" id="inputGroupSelect01">
                        <option>--- 베이스 모델을 골라주세요. ---</option>
                        <option value="1" selected>InceptionV3</option>
                        <option value="2">VGG19 (동작 x)</option>
                        <option value="3">Resnet-50 (동작 x)</option>
                    </select>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from 'axios'

    export default {
        name: 'Inference',

        data() {
            return {
                file: null,
                thumbnail: null,
                isComplate: false,
                predict: null
            }
        },

        methods: {
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
                const file = e.dataTransfer.files[0]
                this.thumbnail = URL.createObjectURL(file)
                this.file = file
            },

            onFileChange(e) {
                const file = e.target.files[0]
                this.thumbnail = URL.createObjectURL(file)
                this.file = file
            },

            deleteImage() {
                this.file = null
                this.thumbnail = null
                this.predict = null
                this.isComplate = null
                this.$refs.fileInput.value = ''
            },

            async inference() {
                let bodyForm = new FormData()
                bodyForm.append('file', this.file)

                let res = await axios.post('/api/inference', bodyForm, {
                    header: {
                        'Content-Type': 'multipart/form-data'
                    },
                    body: {
                        'model': 'base'
                    }
                })

                if (res['data']['success']) {
                    this.isComplate = true
                    let tmp = res['data']['predict']

                    if (!tmp.length) {
                        this.predict = '이미지에서 분류할 대상이 없습니다.'
                    } else {
                        this.predict = `객체명: ${tmp[0][0]}\n정확도: ${tmp[0][1]}%`
                    }
                }
            }
        }
    }
</script>

<style>
    .local {
        max-height: 400px;
        min-height: 400px;
    }

    .preview {
        max-height: 300px;
    }
</style>