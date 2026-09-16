// Validação de formulário
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts após 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            setTimeout(() => {
                if (alert.offsetParent !== null) { // Check if visible
                    alert.style.display = 'none';
                }
            }, 5000);
        }
    });
});

// Formatação de CEP
function formatarCEP(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 5) {
        value = value.substring(0, 5) + '-' + value.substring(5, 8);
    }
    input.value = value;
}

// Formatação de Telefone
function formatarTelefone(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 0) {
        if (value.length <= 2) {
            value = '(' + value;
        } else if (value.length <= 6) {
            value = '(' + value.substring(0, 2) + ') ' + value.substring(2);
        } else {
            value = '(' + value.substring(0, 2) + ') ' + value.substring(2, 7) + '-' + value.substring(7, 11);
        }
    }
    input.value = value;
}

// Formatação de CNPJ
function formatarCNPJ(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 8) {
        value = value.substring(0, 2) + '.' + value.substring(2, 5) + '.' + value.substring(5, 8) + '/' + value.substring(8, 12) + '-' + value.substring(12, 14);
    } else if (value.length > 5) {
        value = value.substring(0, 2) + '.' + value.substring(2, 5) + '.' + value.substring(5);
    } else if (value.length > 2) {
        value = value.substring(0, 2) + '.' + value.substring(2);
    }
    input.value = value;
}

// Suavizar scroll para âncoras
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});