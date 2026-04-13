/// <reference types="vite/client" />

declare module '*.vue' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent<{}, {}, any>
    export default component
}

declare module '*.svg' {
    const content: string
    export default content
}

declare module '*.svg?component' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent
    export default component
}
