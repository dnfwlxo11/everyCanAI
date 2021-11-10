<template>
    <div id="train">
        <div class="container pt-5 pb-5 mt-5 mb-5">
            <div class="">
                <div class="col mb-3"><i class="mdi mdi-home-outline" @click="$router.push({path: '/'})"></i></div>
                    <div class="col-md-12 mb-3">
                        <div class="card">
                            <div v-if="mode=='default'">
                                <button class="btn btn-outline-primary mr-3" @click="mode='local';readFiles()">내 컴퓨터</button>
                                <button class="btn btn-outline-primary" @click="mode=='webcam'">웹캠</button>
                            </div>
                            <div v-else-if="mode=='local'">
                                <input type="file">
                            </div>
                            <div v-else>
                                <div class="camera">
                                    <video id="videoPlayer" width="960" height="720"></video>
                                </div>
                                <div id="camCap">
                                    <canvas id="canvas_vid" style="display: none;"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-12 mb-3">

                    </div>
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header text-left"><h5><strong>모델 정보</strong></h5></div>
                            <div class="card-body">아직 모델을 학습하지 않았습니다.</div>
                        </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Train',

    data() {
        return {
            mode: 'default',
            webCam: null
        }
    },

    methods: {
        readFiles() {
            
        }
    }
}
</script>

<style>
.mdi {
    font-size: 48px;
}
</style>