<template>
  <!-- <HelloWorld /> -->
  <ChatComponent />
</template>

<script>
import { defineComponent } from 'vue';

// Components
// import HelloWorld from '../components/HelloWorld.vue';
import ChatComponent from '@/components/ChatComponent.vue';

export default defineComponent({
  name: 'HomeView',

  components: {
    // HelloWorld,
    ChatComponent,
  },
});
</script>
