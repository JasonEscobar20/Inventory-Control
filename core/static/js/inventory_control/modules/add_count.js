const addInventoryCount = (inventoryId, refreshInventoryCount) => {
    let formInventoryCount = document.getElementById('form_add_inventory_count');
    let inventoryCountFormData = new FormData(formInventoryCount);
    const submitButton = document.getElementById('btn_add_inventory_count');

    inventoryCountFormData.append('inventory', inventoryId);
    inventoryCountFormData.append('active', 'true');

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
            if (submitButton) submitButton.disabled = false;
        })
    })
    .catch(error => {
        console.log({error});
        const detail = error.response?.data;
        let message = 'No se pudo crear el conteo. Verifica los datos e intenta nuevamente.';

        if (detail && typeof detail === 'object') {
            const firstKey = Object.keys(detail)[0];
            const firstValue = Array.isArray(detail[firstKey]) ? detail[firstKey][0] : detail[firstKey];
            if (firstValue) {
                message = String(firstValue);
            }
        }

        swal({
            title: 'Error al guardar',
            text: message,
            icon: 'error',
            button: 'Cerrar',
            closeOnClickOutside: false,
        });
        if (submitButton) submitButton.disabled = false;
    })

}

export {addInventoryCount}
