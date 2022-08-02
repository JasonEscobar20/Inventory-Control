// flatpickr.localize(flatpickr.l10ns.es);
Vue.createApp({
    delimiters: ['{', '}'],
    data() {
        return {
            
        }
    },
    mounted() {
        $("#slc_category").select2({
            width: '100%',
            placeholder: "Seleccione una categoría",
        });
        
    },
    methods: {
        addProduct(){
            let productForm = document.getElementById('form_product');
            let productFormData = new FormData(productForm);

            axios.post('/products/api/create/', productFormData)
            .then(response => {
                swal({
                    title: "Producto agregado",
                    text: "Presiona el botón para continuar",
                    icon: "success",
                    button: "Hecho!",
                })
                .then(value => {
                    location.href = '/products/list/';
                })
            })
            .catch(error => {
                console.log({error})
            })
        }

        
    },
}).mount('#app_product_create')