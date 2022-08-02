flatpickr.localize(flatpickr.l10ns.es);
import {addInventoryCount} from './modules/add_count.js'
Vue.createApp({
    delimiters: ['{', '}'],
    data() {
        return {
            inventoryCounts: [],

            inventoryCountSelected: {
                product: '',
                measurement_unit: '',
                product_status: '',
                amount: '',
                expiration_date: '',
                entry_date: '',
                storage_type: '',
                position: '',
                side: '',
            },
            isDetail: false,
            inventoryCountId: 0,
            inventoryId: 0,
            filtersActive: false
        }
    },
    mounted() {
        this.getInventoryCounts();

        setTimeout(() => {
            $("#slc_product").select2({
                width: '100%',
                placeholder: "Seleccione un producto",
                dropdownParent: $('#create_inventory_count_modal')
            }); 
                
            $("#slc_product1").select2({
                width: '100%',
                placeholder: "Seleccione un producto",
                dropdownParent: $('#create_inventory_count_modal')
            }); 
        }, 500);

        flatpickr(document.getElementById('txt_expiration_date'), {
            dateFormat: 'd-m-Y',
        });
        flatpickr(document.getElementById('txt_entry_date'), {
            dateFormat: 'd-m-Y',
            defaultDate: 'today'
        });

        flatpickr(document.getElementById('txt_expiration_date_2'), {
            dateFormat: 'd-m-Y',
        });
        flatpickr(document.getElementById('txt_entry_date_2'), {
            dateFormat: 'd-m-Y',
        });

        flatpickr(document.getElementById('txt_filter_entry_date'), {
            dateFormat: 'd-m-Y',
        });
        flatpickr(document.getElementById('txt_filter_end_date'), {
            dateFormat: 'd-m-Y',
        });
        
    },
    methods: {
        getInventoryCounts(){
            let url = window.location.pathname;
            let splitUrl = url.split('/');
            let inventoryId = splitUrl[splitUrl.length - 2];

            this.inventoryId = inventoryId;

            axios.get(`/inventory-control/api/counts/list/${inventoryId}/`)
            .then(response => {
                this.inventoryCounts = response.data.results;
            })
        },
        inventoryCountDetail(inventoryCountId, action){
            if (action == 'detail'){ this.isDetail = true; };
            if (action == 'edit'){ this.isDetail = false; };

            this.inventoryCountSetData(inventoryCountId);
        },
        inventoryCountSetData(inventoryCountId){
            let inventoryCountInstance = this.inventoryCounts.filter(item => item.id == inventoryCountId)[0];
            const entryDateFp = document.querySelector("#txt_entry_date_2")._flatpickr;
            const expirationDateFp = document.querySelector("#txt_expiration_date_2")._flatpickr;

            this.inventoryCountSelected = inventoryCountInstance;
            this.inventoryCountId = inventoryCountInstance.id;
            entryDateFp.setDate(inventoryCountInstance.entry_date, true, 'Y-m-d');
            expirationDateFp.setDate(inventoryCountInstance.expiration_date, true, 'Y-m-d');

            $('#slc_product1').val(inventoryCountInstance.product.id).trigger('change');
        },
        editInventoryCount(){
            let formInventoryCount = document.getElementById('form_inventory_count');
            let inventoryCountFormData = new FormData(formInventoryCount);
            let expirationDate = inventoryCountFormData.get('expiration_date');
            let entryDate = inventoryCountFormData.get('entry_date');
            let formatExpirationDate = moment(expirationDate, 'DD-MM-Y').format('Y-MM-DD');
            let formatEntryDate = moment(entryDate, 'DD-MM-Y').format('Y-MM-DD');
            let inventoryCountId = this.inventoryCountId;
            let token = document.querySelector('input[name=csrfmiddlewaretoken]').value;

            inventoryCountFormData.set('entry_date', formatEntryDate);
            inventoryCountFormData.set('expiration_date', formatExpirationDate);

            axios.patch(`/inventory-control/api/count/update/${inventoryCountId}/`, inventoryCountFormData, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': token,
                }
            })
            .then(response => {
                document.getElementById('btn_close_inventory_count_detail').click();
                swal({
                    title: "Conteo editado",
                    text: "Presiona el botón para continuar",
                    icon: "success",
                    button: "Cerrar!",
                    closeOnClickOutside: false,
                    closeOnClickOutside: false,
                })
                .then(value => {
                    this.getInventoryCounts();
                    
                })
            })
            .catch(error => {
                console.log({error});
            })
        },
        closeInventoryCountModal(){
            this.isDetail = false;
            const entryDateFp = document.querySelector("#txt_entry_date")._flatpickr;
            const expirationDateFp = document.querySelector("#txt_expiration_date")._flatpickr;

            entryDateFp.clear();
            expirationDateFp.clear();

            this.inventoryCountSelected = {
                product: '',
                measurement_unit: '',
                product_status: '',
                amount: '',
                expiration_date: '',
                entry_date: '',
                storage_type: '',
                position: '',
                side: '',
            }
        },
        addInventoryCounter(){
            addInventoryCount(this.inventoryId, 'refresh')
        },

        filterInventoryCounts(){
            let $form = document.getElementById('form_filter_inventory_counts');
            let formData = new FormData($form);
            let token = document.querySelector('input[name=csrfmiddlewaretoken]').value;
            let filters = {}

            for (let item of formData.entries()){
                let key = item[0];
                let value = item[1];

                if (value != ''){
                    if (key == 'entry_date'){
                        let entryDate = value;
                        let formatEntryDate = moment(entryDate, 'DD-MM-Y').format('Y-MM-DD');
                        filters['entry_date'] = formatEntryDate;
                    }
                    else if (key == 'end_date' != ''){
                        let endDate = value;
                        let formatEndDate = moment(endDate, 'DD-MM-Y').format('Y-MM-DD');
                        formData.set('end_date', formatEndDate);
                    }
                    else {
                        filters[key] = value;
                    }
                }
            };
            

            axios.post('/inventory-control/api/count/filter/', filters, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': token,
                }
            })
            .then(response => {
                this.filtersActive = true;
                this.inventoryCounts = response.data;
                document.getElementById('btn_close_modal_filter').click();
            })
            .catch(error => {
                console.log({error});
            })
        },
        cleanFilters(){
            this.filtersActive = false;
            this.getInventoryCounts();
            let $form = document.getElementById('form_filter_inventory_counts');
            $form.reset();

        },
        generateReport(){
            let params = {};
            let filterForm = document.getElementById('form_filter_inventory_counts');
            let filtersFormData = new FormData(filterForm);

            if (this.filtersActive){
                for (let item of filtersFormData.entries()){
                    let key = item[0];
                    let value = item[1];

                    if (value != '' && key != 'csrfmiddlewaretoken'){
                        params[key] = value;
                    }
                }
            }
            // document.getElementById('btn_generate_report').classList.add('running');
            // document.getElementById('btn_generate_report').setAttribute('disabled', true);
           

            axios({
                url: `/inventory-control/generate/inventory_count/report/`,
                method: 'get',
                contentType: 'application/json',
                params: params,
                responseType: 'blob'
            })
            .then(response => {

                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                let name = response.headers['content-disposition'].split('filename=')[1];
                link.href = url;
                link.setAttribute('download', name);
                document.body.appendChild(link);
                link.click();
            })
            .catch(error => {
                if (error.response.status == 400){
                    alert('No existen registros para realizar el reporte');
                }
            });
        }

        
    },
}).mount('#app_inventory_count')