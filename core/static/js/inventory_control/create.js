// flatpickr.localize(flatpickr.l10ns.es);
Vue.createApp({
    delimiters: ['{', '}'],
    data() {
        return {
            
        }
    },
    mounted() {
        $("#slc_warehouse").select2({
            width: '100%',
            placeholder: "Seleccione una bodega",
            allowClear: true,
        });
        $("#slc_employee").select2({
            width: '100%',
            placeholder: "Seleccione un empleado",
            allowClear: true,
        }); 
    },
    methods: {
        startInventory(){
            let inventoryForm = document.getElementById('form_inventory');
            let inventoryFormData = new FormData(inventoryForm);

            axios.post('/inventory-control/api/create/', inventoryFormData)
            .then(response => {
                swal({
                    title: "Inventario creado",
                    text: "Presiona el botón para continuar",
                    icon: "success",
                    button: "Hecho!",
                })
                .then(value => {
                    location.href = '/inventory-control/list/';
                })
            })
            .catch(error => {
                console.log({error})
            })
        }

        
    },
}).mount('#app_product_create')