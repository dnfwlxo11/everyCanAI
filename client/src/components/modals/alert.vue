<template>
  <transition name="modal">
    <div class="modal-mask">
      <div class="modal-wrapper">
        <div class="modal-container">
          <div class="modal-header justify-content-end">
            <a href="javascript:;" class="btn btn-sm" @click="$emit('on-confirm')">
              <i class="mdi mdi-close"></i>
            </a>
          </div>
          <div class="modal-body">
            <div class="text-center pb-3" v-html="msg"></div>
          </div>  
          <div class="modal-footer d-block">
            <div class="row">
              <div class="col-md-4 ml-auto mr-auto">
                <button type="button" class="btn btn-sm btn-block" @click="$emit('on-confirm')">
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
  name: 'AlertModal',  
  props: {    
    msg: {
      type: String,
      default: ''
    }
  },
  methods: {
    escCloseListener(evt) {           
      if(evt.key != 'Escape') return false
      this.$emit('on-close')
    },
  },
  mounted () {
    window.addEventListener('keydown', this.escCloseListener)
    document.documentElement.style.overflowY = 'hidden'
  },
  destroyed () {
    window.removeEventListener('keydown', this.escCloseListener, false)
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