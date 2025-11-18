const addInventoryCount = (inventoryId, refreshInventoryCount) => {
    let formInventoryCount = document.getElementById('form_add_inventory_count');
    let inventoryCountFormData = new FormData(formInventoryCount);

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