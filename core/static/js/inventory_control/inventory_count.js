flatpickr.localize(flatpickr.l10ns.es);
import {addInventoryCount} from './modules/add_count.js'
Vue.createApp({
    delimiters: ['{', '}'],
    data() {
        return {
            pagination: {
                pages: 0,
                previous: null,
                next: null,
                activePage: 1,
                use_pagination: false,
            },
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
            filters: {},
            showImageField: false,
            productSelectInitialized: false,
            productEditSelectInitialized: false,
        }
    },
    mounted() {
        this.getInventoryCounts();

        this.initProductSelect();
        this.initProductEditSelect();
        
        setTimeout(() => {
            document.getElementById('btn-open-count-modal').click();
        }, 500);

        const createModal = document.getElementById('create_inventory_count_modal');
        if (createModal) {
            createModal.addEventListener('shown.bs.modal', () => {
                this.initProductSelect();
            });
        }

        const editModal = document.getElementById('inventoryCount');
        if (editModal) {
            editModal.addEventListener('shown.bs.modal', () => {
                this.initProductEditSelect();
            });
        }
    },
    methods: {
        initAjaxProductSelect(selectId, dropdownParentSelector, initializedFlag){
            if (this[initializedFlag]) return;

            const productSelect = document.getElementById(selectId);
            if (!productSelect) return;

            $(productSelect).select2({
                width: '100%',
                placeholder: 'Seleccione un producto',
                dropdownParent: $(dropdownParentSelector),
                ajax: {
                    url: '/products/api/list/',
                    dataType: 'json',
                    delay: 250,
                    data: function (params) {
                        return {
                            search: params.term || '',
                            q: params.term || '',
                            page: params.page || 1,
                        };
                    },
                    processResults: function (data, params) {
                        params.page = params.page || 1;
                        return {
                            results: data.results.map(item => ({
                                id: item.id,
                                text: `${item.sku} ${item.description}`.trim(),
                            })),
                            pagination: {
                                more: data.next !== null,
                            }
                        };
                    },
                    cache: true
                },
                minimumInputLength: 0,
            });

            this[initializedFlag] = true;
        },
        initProductSelect(){
            this.initAjaxProductSelect('slc_product', '#create_inventory_count_modal', 'productSelectInitialized');
        },
        initProductEditSelect(){
            this.initAjaxProductSelect('slc_product1', '#inventoryCount', 'productEditSelectInitialized');
        },
        buildInventoryCountParams(page = 1){
            let params = new URLSearchParams();
            params.set('page', page);

            if (this.filtersActive){
                if (this.filters.sku) params.set('sku', this.filters.sku);
                if (this.filters.product_status) params.set('product_status', this.filters.product_status);
                if (this.filters.storage_type) params.set('storage_type', this.filters.storage_type);
            }

            return params;
        },
        loadInventoryCounts(page = 1){
            this.pagination.use_pagination = true;

            const params = this.buildInventoryCountParams(page);
            axios.get(`/inventory-control/api/counts/list/${this.inventoryId}/?${params.toString()}`)
            .then(response => {
                this.inventoryCounts = response.data.results;
                this.pagination.previous = response.data.previous;
                this.pagination.next = response.data.next;
                this.pagination.pages = Math.ceil(response.data.count / 20);
                this.pagination.activePage = page;
                this.pagination.use_pagination = false;
            })
            .catch(error => {
                console.log({error});
                this.pagination.use_pagination = false;
            })
        },
        previousNextPage(page, action){
            this.pagination.use_pagination = true;
            axios.get(page)
            .then(response => {
                if (action == 0){
                    this.pagination.activePage -= 1;
                }
                if (action == 1){
                    this.pagination.activePage += 1;
                }

                this.pagination.previous = response.data.previous;
                this.pagination.next = response.data.next;
                this.pagination.pages = Math.ceil(response.data.count / 20);
                this.inventoryCounts = response.data.results;
                this.pagination.use_pagination = false;
            })
            .catch(error => {
                console.log({error});
                this.pagination.use_pagination = false;
            })
        },
        selectPage(number){
            this.loadInventoryCounts(number);
        },
        getInventoryCounts(){
            let url = window.location.pathname;
            let splitUrl = url.split('/');
            let inventoryId = splitUrl[splitUrl.length - 2];

            this.inventoryId = inventoryId;
            this.loadInventoryCounts(1);
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

            this.initProductEditSelect();

            const productId = inventoryCountInstance.product.id;
            const productLabel = `${inventoryCountInstance.product.sku} ${inventoryCountInstance.product.description}`.trim();
            const productSelect = $('#slc_product1');
            const currentOption = productSelect.find(`option[value="${productId}"]`);

            if (!currentOption.length) {
                const option = new Option(productLabel, productId, true, true);
                productSelect.append(option);
            }

            productSelect.val(productId).trigger('change');
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
        deleteInventoryCount(inventoryCountId){
            if(!confirm('¿Eliminar este conteo? Se desactivará sin borrarse definitivamente.')) return;

            let token = document.querySelector('input[name=csrfmiddlewaretoken]').value;
            axios.post(`/inventory-control/api/count/delete/${inventoryCountId}/`, {}, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': token,
                }
            })
            .then(response => {
                swal({
                    title: 'Conteo desactivado',
                    text: 'El registro fue marcado como inactivo.',
                    icon: 'success',
                    button: 'Cerrar',
                    closeOnClickOutside: false,
                }).then(() => {
                    this.getInventoryCounts();
                });
            })
            .catch(error => {
                console.log({error});
                alert(error.response?.data?.detail || 'No fue posible eliminar el conteo.');
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
            document.getElementById('btn_add_inventory_count').disabled = true;
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
            let filters = {}

            for (let item of formData.entries()){
                let key = item[0];
                let value = item[1];

                if (value != ''){
                    filters[key] = value;
                }
            };

            this.filters = filters;
            this.filtersActive = Object.keys(this.filters).length > 0;
            this.pagination.activePage = 1;
            document.getElementById('btn_close_modal_filter').click();
            this.loadInventoryCounts(1);
        },
        cleanFilters(){
            this.filtersActive = false;
            this.filters = {};
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
