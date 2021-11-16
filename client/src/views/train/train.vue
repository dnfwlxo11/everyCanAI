<template>
    <div id="train">
        <div class="container pt-3 pb-5 mt-5 mb-5 vh-100">
            <!-- <div ref="mode" class="btn-group btn-group-toggle mb-3" data-toggle="buttons" @change="getMode">
                <label class="btn btn-outline-primary active">
                    <input type="radio" name="options" id="option1" checked> 로컬
                </label>
                <label class="btn btn-outline-primary">
                    <input type="radio" name="options" id="option2"> 웹캠
                </label>
            </div> -->
            <local v-if="mode=='local'"></local>
            <cam v-else></cam>

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
</template>

<script>
    import axios from 'axios'
    import Local from './vues/local'
    import Cam from './vues/cam'

    export default {
        name: 'Train',

        components: {
            Local,
            Cam
        },

        data() {
            return {
                mode: 'local',
                modelInfo: null,
            }
        },

        mounted() {
            this.getModel()
        },

        methods: {
            async getModel() {
                let res = await axios.get('/api/information')
                this.modelInfo = res.data.info
            },

            getMode() {
                console.log(this.$refs.mode.focus)
            }
        }
    }
</script>

<style>
    html,
    body {
        height: 100%;
        margin: 0;
        overflow: hidden;
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