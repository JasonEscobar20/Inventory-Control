const addInventoryCount = (inventoryId, refreshInventoryCount) => {
    let formInventoryCount = document.getElementById('form_add_inventory_count');
    let inventoryCountFormData = new FormData(formInventoryCount);

    let expirationDate = inventoryCountFormData.get('expiration_date');
    let entryDate = inventoryCountFormData.get('entry_date');
    let formatExpirationDate = moment(expirationDate, 'DD-MM-Y').format('Y-MM-DD');
    let formatEntryDate = moment(entryDate, 'DD-MM-Y').format('Y-MM-DD');

    inventoryCountFormData.set('entry_date', formatEntryDate);
    inventoryCountFormData.set('expiration_date', formatExpirationDate);
    inventoryCountFormData.append('inventory', inventoryId);

    axios.post(`/inventory-control/api/count/create/`, inventoryCountFormData)
    .then(response => {
        
        swal({
            title: "Conteo agregado",
            text: "Presiona el botón para continuar",
            icon: "success",
            button: "Cerrar!",
            closeOnClickOutside: false,
            closeOnClickOutside: false,
        })
        .then(value => {
            console.log('prueba')
            if (refreshInventoryCount == 'refresh'){
                location.reload();
            }
            document.getElementById('btn_close_add_inventory_count').click();
        })
    })
    .catch(error => {
        console.log({error});
    })

}

export {addInventoryCount}