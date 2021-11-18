<template>
  <div class="home">
    <div class="container pt-5 pb-5 mt-5 mb-5 h-100">
      <div class="row h-100">
        <div class="col-md-4">
          <div class="card d-flex align-items-center justify-content-center basic" @click="$router.push({path: 'inference'})">
            <div class="text-left">
              <strong>기본 모델로 이미지를 분류하고 싶어요.</strong><br>
              이미지 포맷을 업로드하면 됩니다.
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card d-flex align-items-center justify-content-center  custom" @click="$router.push({path: 'train'})">
            <div class="text-left">
              <strong>내가 원하는 모델을 만들고 싶어요.</strong><br>
              클래스당 30장 이상의 사진이 필요합니다.
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card d-flex align-items-center justify-content-center  custom" @click="$router.push({path: 'models'})">
            <div class="text-left">
              <strong>모델 저장소</strong><br>
              나의 학습 모델들을 확인할 수 있습니다.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// @ is an alias to /src

export default {
  name: 'Models'
}
</script>

<style>
  html,
  body {
      height: 100%;
      margin: 0;
  }

  .basic, .custom {
    height: 35vw;
    font-size: 1.1rem;
  }
</style>
pt>
