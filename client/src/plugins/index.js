import alertModal from '@/components/modals/alert'
import confirmModal from '@/components/modals/confirm'
import progressModal from '@/components/modals/progress'

export default {
    install(Vue) {
        //global components
        Vue.component('alert-modal', alertModal)
        Vue.component('confirm-modal', confirmModal)
        Vue.component('progress-modal', progressModal)
    }
}