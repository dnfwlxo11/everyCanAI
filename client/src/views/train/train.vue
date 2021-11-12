<template>
    <div id="train">
        <div class="btn-group btn-group-toggle mt-3" data-toggle="buttons">
            <label class="btn btn-outline-primary active">
                <input type="radio" name="options" id="option1" checked> 로컬
            </label>
            <label class="btn btn-outline-primary">
                <input type="radio" name="options" id="option2"> 웹캠
            </label>
        </div>
        <local v-if="mode=='local'"></local>
        <cam v-else></cam>
    </div>
</template>

<script>
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
            mode: 'local'
        }
    },

    mounted() {
    },

    methods: {
        
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