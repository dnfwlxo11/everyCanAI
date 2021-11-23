<template>
  <transition name="modal">
    <div class="modal-mask">
      <div class="modal-wrapper">
        <div class="modal-container">          
          <div class="modal-body">
            <div class="text-center p-3">
              <i class="mdi mdi-loading mdi-spin mr-2"></i>
              <span>{{ msg }}</span>
            </div>
          </div>            
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'ProgressModal',  
  props: {    
    msg: {
      type: String,
      default: '진행 중...'
    }
  },
  mounted () {
    document.documentElement.style.overflowY = 'hidden'
  },
  destroyed () {
    document.documentElement.style.overflowY = 'auto'
  }, 
}
</script>


<style lang="scss" scoped>  
  .modal-container{
    max-width: 480px;
    margin-top: 100px;
  }
</style>