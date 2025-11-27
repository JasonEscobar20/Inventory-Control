// flatpickr.localize(flatpickr.l10ns.es);
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

            products: [],
            filterActive: false,
            filters: {}
        }
    },
    mounted() {
        this.getProductList();
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
                this.products = response.data.results;
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
            

            axios.get(`/products/api/list/?page=${number}`)
            .then(response => {
                document.getElementById(`li_${number}`).classList.add('active');    
                this.pagination.previous = response.data.previous;
                this.pagination.next = response.data.next;
                this.pagination.pages = Math.ceil(response.data.count / 20);
                this.products = response.data.results;
                this.pagination.use_pagination = false;
            })
            .catch(error => {
                console.log({error});
            })
        },

        getProductList(){
            axios.get('/products/api/list/')
            .then(response => {
                
                this.products = response.data.results;
                this.pagination.previous = response.data.previous;
                this.pagination.next = response.data.next;
                this.pagination.pages = Math.ceil(response.data.count / 20);
                
            })
            .catch(error => {
                console.log({error})
            })
        },
        filterProducts(){
            let $form = document.getElementById('form_filter_products');
            let formData = new FormData($form);
            this.filters = {
                brand: formData.get('brand') || ''
            };
            axios.post('/products/api/filter/', formData)
            .then(response => {
                this.filterActive = true;
                this.products = response.data;
                document.getElementById('btn_close_modal_filter').click();
            })
            .catch(error => {
                console.log({error});
            })
        },
        exportHref(format){
            const params = new URLSearchParams();
            params.set('format', format || 'xlsx');
            if (this.filters.brand) params.set('brand', this.filters.brand);
            return `/products/export/?${params.toString()}`;
        }
    },

}).mount('#app_product_list')