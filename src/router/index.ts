import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import PricingView from '../views/PricingView.vue';
import ContactView from '../views/ContactView.vue';
import GiveawayView from '../views/GiveawayView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/pricing',
      name: 'pricing',
      component: PricingView
    },
    {
      path: '/contact',
      name: 'contact',
      component: ContactView
    },
    {
      path: '/giveaway',
      name: 'giveaway',
      component: GiveawayView
    }
    
  ],
  // Aggiungi questa configurazione per il comportamento dello scroll
  scrollBehavior(to, _from, savedPosition) {
    // Se l'utente utilizza il pulsante indietro/avanti e c'è una posizione salvata
    if (savedPosition) {
      return savedPosition;
    }
    
    // Controlla se la rotta di destinazione ha un hash (anchor)
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth', // scroll fluido
        top: 80, // offset opzionale se hai una navbar fissa
      };
    }
    
    // Altrimenti, torna in cima alla pagina
    return { top: 0, behavior: 'smooth' };
  }
});

export default router;