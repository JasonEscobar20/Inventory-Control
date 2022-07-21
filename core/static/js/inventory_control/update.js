// flatpickr.localize(flatpickr.l10ns.es);
Vue.createApp({
    delimiters: ['{', '}'],
    data() {
        return {
            
        }
    },
    mounted() {

        let $store_value = document.getElementById('txt_store').value;
        let $employee_value = document.getElementById('txt_employee').value;

        $("#slc_employee").select2({
            width: '100%',
            placeholder: "Seleccione un empleado",
            allowClear: true,
        });

        $("#slc_store").select2({
            width: '100%',
            placeholder: "Seleccione un almacen",
            allowClear: true,
        });
        
        setTimeout(() => {
            $('#slc_store').val($store_value).trigger('change');
            $('#slc_employee').val($employee_value).trigger('change');
        }, 200);
    },
}).mount('#app_update_product')