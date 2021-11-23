<template>
  <transition name="modal">
    <div class="modal-mask">
      <div class="modal-wrapper">
        <div class="modal-container">
          <div class="modal-header justify-content-end">
            <a href="javascript:;" class="btn btn-sm" @click="$emit('on-close')">
              <i class="mdi mdi-close"></i>
            </a>
          </div>
          <div class="modal-body">
            <div class="text-center pb-3" v-html="msg"></div>
          </div>  
          <div class="modal-footer d-block">
            <div class="row">
              <div class="col-md-4 col-6 ml-auto">
                <button type="button" class="btn btn-sm btn-block text-secondary" @click="$emit('on-close')">
                  <i class="mdi mdi-close"></i> 취소
                </button>
              </div>
              <div class="col-md-4 col-6 mr-auto">
                <button type="button" class="btn btn-sm btn-block text-success" @click="$emit('on-confirm')">
                  <i class="mdi mdi-check"></i> 확인
                </button>
              </div>
            </div>
          </div>                          
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'ConfirmModal',  
  props: {    
    msg: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      // 중복이벤트발생 방지 변수
      isProcessing: false
    }
  },
  methods: {
    keyEvtListener(evt) {      
      const AllowKeys = ['Enter','Escape']
      const findIdx = AllowKeys.indexOf(evt.key)
      if(findIdx < 0 || this.isProcessing) return false
      this.isProcessing = true
      if(findIdx == 0){
        this.$emit('on-confirm')
      }else{
        this.$emit('on-close')
      }
      this.isProcessing = false
    },
  },
  mounted () {
    window.addEventListener('keyup', this.keyEvtListener)
    document.documentElement.style.overflowY = 'hidden'
  },
  destroyed () {
    window.removeEventListener('keyup', this.keyEvtListener, false)
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