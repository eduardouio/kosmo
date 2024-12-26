import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const useColorsStore = defineStore("colorsStore", {
    state: () => ({
        colors: {
                'AMARILLO': 'bg-yellow-400 bg-gradient',
                'CREMA': 'bg-amber-400 bg-gradient',
                'ROJO': 'bg-red-400 bg-gradient',
                'BLANCO': 'bg-light',
                'TINTURADO': 'bg-gray-400 bg-gradient',
                'NARANJA': 'bg-orange-400 bg-gradient',
                'VIOLETA': 'bg-indigo-400 bg-gradient',
                'MORADO': 'bg-indigo-400 bg-gradient',
            },
    }),
});