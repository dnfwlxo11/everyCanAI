<template>
    <div id="inference">
        <div class="container pt-5 pb-5 mt-5 mb-5">
            <div class="row mb-3">
                <div class="col mb-3"><i class="mdi mdi-home-outline" @click="$router.push({path: '/'})"></i></div>
                <!-- <button class="btn btn-primary" @click="printImage">출력</button> -->
            </div>
            <div class="row align-items-center">
                <div class="col-md-5">
                    <div class="card">
                        <div class="card-header">
                            <strong>분류하고 싶은 사진</strong> <small>(Model. resnet50)</small>
                        </div>
                        <div class="card-body" style="min-height: 400px">

                        </div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div>
                        <i class="mdi mdi-arrow-right-bold-outline" style="font-size:48px;"></i>
                    </div>
                    <div>
                        <button class="btn btn-outline-primary">분류하기</button>
                    </div>
                </div>
                <div class="col-md-5">
                    <div class="card">
                        <div class="card-header">
                            <strong>분류 결과</strong>
                        </div>
                        <div class="card-body" style="min-height: 400px">

                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Inference'
}
</script>