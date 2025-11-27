// flatpickr.localize(flatpickr.l10ns.es);
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
            inventoryId: 0,
            inventories: [],
            filtersActive: false,
            filters: {}
        }
    },
    mounted() {
        this.getInventoryList();

        setTimeout(() => {
            // __________MODAL
            // showing modal with effect
            this.showModalWithEffect();

            let tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
	        var tooltipList = tooltipTriggerList.forEach(element => {
		        return new bootstrap.Tooltip(element)
	        })
        }, 500);

        // flatpickr(document.getElementById('txt_expiration_date'), {
        //     dateFormat: 'd-m-Y',
        // });
        // flatpickr(document.getElementById('txt_entry_date'), {
        //     dateFormat: 'd-m-Y',
        // });

        $("#slc_product").select2({
            width: '100%',
            placeholder: "Seleccione un producto",
            dropdownParent: $('#create_inventory_count_modal')
        }); 
        
    },
    
    methods: {
        previousNextPage(page, action){
            this.pagination.use_pagination = true;
            axios.get(page)
            .then(response => {
                
                document.getElementById(`li_${this.pagination.activePage}`).classList.remove("active");
                if (action == 0){
                    this.pagination.activePage = this.pagination.activePage -= 1;
                } 
                if (action == 1){
                    this.pagination.activePage = this.pagination.activePage += 1;
                }

                this.pagination.previous = response.data.previous;
                this.pagination.next = response.data.next;
                document.getElementById(`li_${this.pagination.activePage}`).classList.add("active");
                this.pagination.pages = Math.ceil(response.data.count / 20);
                this.inventories = response.data.results;
                this.pagination.use_pagination = false;
            })
            .catch(error => {
                console.log({error});
            })
        },
        selectPage(number){
            this.pagination.use_pagination = true;
            this.pagination.activePage = number
            
            document.querySelector('.pagination li.active').classList.remove('active')
            
            let params = new URLSearchParams();
            params.set('page', number);
            axios.get(`/inventory-control/api/list/?${params.toString()}`)
            .then(response => {
                document.getElementById(`li_${number}`).classList.add('active');    
                this.pagination.previous = response.data.previous;
                this.pagination.next = response.data.next;
                this.pagination.pages = Math.ceil(response.data.count / 20);
                this.inventories = response.data.results;
                this.pagination.use_pagination = false;
            })
            .catch(error => {
                console.log({error});
            })
        },
        showModalWithEffect(){
            $('.modal-effect').on('click', function(e) {
                e.preventDefault();
                console.log('entra')
                var effect = $(this).attr('data-bs-effect');
                $('.modal-with-effect').addClass(effect);
            });
            // hide modal with effect
            $('.modal-with-effect').on('hidden.bs.modal', function(e) {
                $(this).removeClass(function(index, className) {
                    return (className.match(/(^|\s)effect-\S+/g) || []).join(' ');
                });
            }); 
        },
        getInventoryCounts(){
            console.log('agregado correctamente');
        },
        getInventoryList(){
            let params = new URLSearchParams();
            if (this.filtersActive){
                if (this.filters.warehouse) params.set('warehouse', this.filters.warehouse);
                if (this.filters.employee) params.set('employee', this.filters.employee);
                if (this.filters.date) params.set('date', this.filters.date);
            }
            const url = params.toString() ? `/inventory-control/api/list/?${params.toString()}` : '/inventory-control/api/list/';
            axios.get(url)
            .then(response => {
                
                this.inventories = response.data.results;
                this.pagination.previous = response.data.previous;
                this.pagination.next = response.data.next;
                this.pagination.pages = Math.ceil(response.data.count / 20);
                console.log(this.pagination.pages)
            })
            .catch(error => {
                console.log({error})
            })
        },
        saveInventoryId(id){
            this.inventoryId = id;
        },
        addInventoryCounter(){
            
            addInventoryCount(this.inventoryId);
        },
        filterInventories(){
            const form = document.getElementById('form_filter_inventories');
            const formData = new FormData(form);
            this.filters = {
                warehouse: formData.get('warehouse') || '',
                employee: formData.get('employee') || '',
                date: formData.get('date') || '',
            };
            // Remove empties
            Object.keys(this.filters).forEach(k => { if (!this.filters[k]) delete this.filters[k]; });
            this.filtersActive = Object.keys(this.filters).length > 0;
            document.getElementById('btn_close_inventory_filters').click();
            this.pagination.activePage = 1;
            this.getInventoryList();
        }
    },
}).mount('#app_product_list')