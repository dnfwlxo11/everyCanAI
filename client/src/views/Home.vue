<template>
  <div class="home">
    <div class="container pt-5 pb-5 mt-5 mb-5">
      <div class="row">
        <div class="col-md-6">
          <div class="card basic" @click="$router.push({path: 'inference'})">
            <div class="card-body text-left mt-5">
              <h3><strong>기본 모델로 이미지를 분류하고 싶어요.</strong></h3>
              <h5>이미지 포맷을 업로드하면 됩니다.</h5>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card custom" @click="$router.push({path: 'train'})">
            <div class="card-body text-left mt-5">
              <h3><strong>내가 원하는 모델을 만들고 싶어요.</strong></h3>
              <h5>클래스당 30장 이상의 사진이 필요합니다.</h5>
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
  name: 'Home'
}
</script>

<style>
  .basic, .custom {
    min-height: 700px;
  }
</style>
pt>
