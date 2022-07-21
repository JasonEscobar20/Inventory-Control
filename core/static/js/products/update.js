// flatpickr.localize(flatpickr.l10ns.es);
Vue.createApp({
    delimiters: ['{', '}'],
    data() {
        return {
            
        }
    },
    mounted() {

        let $category_value = document.getElementById('txt_category').value;

        $("#slc_category").select2({
            width: '100%',
            placeholder: "Seleccione una categoría",
            allowClear: true,
        });
        
        setTimeout(() => {
            $('#slc_category').val($category_value).trigger('change');
        }, 200);
    },
}).mount('#app_update_product')