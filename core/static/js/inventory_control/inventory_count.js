flatpickr.localize(flatpickr.l10ns.es);
import {addInventoryCount} from './modules/add_count.js'
Vue.createApp({
    delimiters: ['{', '}'],
    data() {
        return {
            inventoryCounts: [],

            inventoryCountSelected: {
                product: '',
                product_status: '',
                amount: '',
                storage_type: '',
                position: '',
                position_letter: '',
            },
            isDetail: false,
            inventoryCountId: 0,
            inventoryId: 0,
            filtersActive: false,
            showImageField: false,
        }
    },
    mounted() {
        this.getInventoryCounts();

        setTimeout(() => {
            // $("#slc_product").select2({
            //     width: '100%',
            //     placeholder: "Seleccione un producto",
            //     dropdownParent: $('#create_inventory_count_modal')
            // }); 
            $("#slc_product").selectize({
                sortField: "text",
              });
                
            $("#slc_product1").select2({
                width: '100%',
                placeholder: "Seleccione un producto",
                dropdownParent: $('#create_inventory_count_modal')
            }); 
        }, 500);
        
    },
    methods: {
        getInventoryCounts(){
            let url = window.location.pathname;
            let splitUrl = url.split('/');
            let inventoryId = splitUrl[splitUrl.length - 2];

            this.inventoryId = inventoryId;

            axios.get(`/inventory-control/api/counts/list/${inventoryId}/`)
            .then(response => {
                console.log({response});
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
            this.inventoryCountSelected = inventoryCountInstance;
            this.inventoryCountId = inventoryCountInstance.id;

            $('#slc_product1').val(inventoryCountInstance.product.id).trigger('change');
        },
        editInventoryCount(){
            let formInventoryCount = document.getElementById('form_inventory_count');
            let inventoryCountFormData = new FormData(formInventoryCount);
            let inventoryCountId = this.inventoryCountId;
            let token = document.querySelector('input[name=csrfmiddlewaretoken]').value;

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

            this.inventoryCountSelected = {
                product: '',
                product_status: '',
                amount: '',
                storage_type: '',
                position: '',
                position_letter: '',
            }
        },
        addInventoryCounter(){
            addInventoryCount(this.inventoryId, 'refresh')
        },

        productStatusChange(event){
            let selectedValue = event.target.value;
            console.log(selectedValue == 3);

            if (selectedValue == 3 ){
                this.showImageField = true;
            }
            else {
                this.showImageField = false;
            }
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

                    if (key == 'end_date' != ''){
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
                    console.log(item)
                    let key = item[0];
                    let value = item[1];

                    if (value != '' && key != 'csrfmiddlewaretoken'){
                        params[key] = value;
                    }
                }   
            }
            // document.getElementById('btn_generate_report').classList.add('running');
            // document.getElementById('btn_generate_report').setAttribute('disabled', true);
            params['inventory_id'] = this.inventoryId;

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
        },
        finalizeInventory(){
            if(!confirm('¿Marcar inventario como Finalizado?')) return;
            const token = document.querySelector('input[name=csrfmiddlewaretoken]').value;
            axios.post(`/inventory-control/api/status/update/${this.inventoryId}/`, {status:2}, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': token,
                }
            }).then(resp => {
                swal({title:'Inventario finalizado', icon:'success', button:'Cerrar'}).then(()=>{ location.reload(); });
            }).catch(err => {
                alert(err.response?.data?.detail || 'Error al finalizar');
            })
        }
        ,confirmInventory(){
            if(!confirm('¿Confirmar inventario? Esta acción es definitiva.')) return;
            const token = document.querySelector('input[name=csrfmiddlewaretoken]').value;
            axios.post(`/inventory-control/api/status/update/${this.inventoryId}/`, {status:3}, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': token,
                }
            }).then(resp => {
                swal({title:'Inventario confirmado', icon:'success', button:'Cerrar'}).then(()=>{ location.reload(); });
            }).catch(err => {
                alert(err.response?.data?.detail || 'Error al confirmar');
            })
        }

        
    },
}).mount('#app_inventory_count')