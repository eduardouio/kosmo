import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Creamos Pinia y añadimos un plugin para observar cambios en stagesLoaded
const pinia = createPinia();
pinia.use(({ store }) => {
	if (store.$id === 'baseStore') {
		let prev = store.stagesLoaded;
		store.$subscribe((mutation, state) => {
			if (state.stagesLoaded !== prev) {
				console.log(`[baseStore] stagesLoaded: ${prev} -> ${state.stagesLoaded}`);
				prev = state.stagesLoaded;
			}
		}, { detached: true });
	}
});

const app = createApp(App)

app.use(pinia)
app.use(router)

app.mount('#appVue')
