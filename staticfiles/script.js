// Orascom Go - script.js
// يحوي معالجة الطلب بدون تسجيل، تتبع الشحنة، التابات، وحماية للـ loading

document.addEventListener('DOMContentLoaded', () => {
    // =========================
    // 1. الطلب بدون تسجيل (guest-order-form)
    // =========================
    const guestForm = document.getElementById('guest-order-form');
    const submitBtn = guestForm ? document.getElementById('submit-guest-order') : null;
    const spinner = submitBtn ? submitBtn.querySelector('.spinner') : null;
    const loading = document.getElementById('loading');
  
    if (guestForm && submitBtn && spinner) {
      guestForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        submitBtn.disabled = true;
        spinner.style.display = 'inline-block';
        if (loading) loading.style.display = 'block';
  
        // جمع بيانات الطلب
        const orderData = {
          customer_name: guestForm.querySelector('#order-name') ? guestForm.querySelector('#order-name').value : '',
          customer_phone: guestForm.querySelector('#order-phone') ? guestForm.querySelector('#order-phone').value : '',
          from_area: guestForm.querySelector('#order-from') ? guestForm.querySelector('#order-from').value : '',
          to_area: guestForm.querySelector('#order-to') ? guestForm.querySelector('#order-to').value : '',
          pickup_address: guestForm.querySelector('#order-address') ? guestForm.querySelector('#order-address').value : '',
          delivery_address: guestForm.querySelector('#order-address') ? guestForm.querySelector('#order-address').value : '',
          weight: guestForm.querySelector('#order-weight') ? parseFloat(guestForm.querySelector('#order-weight').value) : 0,
          service_type: guestForm.querySelector('#order-service-type') ? guestForm.querySelector('#order-service-type').value : '',
          notes: guestForm.querySelector('#order-notes') ? guestForm.querySelector('#order-notes').value : '',
          payment_method: guestForm.querySelector('input[name="payment"]:checked') ? guestForm.querySelector('input[name="payment"]:checked').value : ''
        };
  
        try {
          const response = await fetch('/api/orders/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
          });
        
          const result = await response.json();
          if (response.ok) {
            alert(`تم إنشاء الطلب بنجاح!\nرقم التتبع: ${result.tracking_number || ''}`);
            guestForm.reset();
          } else {
            alert('حصل خطأ: ' + (result.detail || JSON.stringify(result)));
          }
        } catch (err) {
          alert('فشل الاتصال');
        } finally {
          submitBtn.disabled = false;
          spinner.style.display = 'none';
        }
      });
    }
  
    // =========================
    // 2. التابات للتبديل بين تتبع برقم التتبع/الهاتف
    // =========================
    const tabs = document.querySelectorAll('.track-tab-btn');
    const trackingFormNumber = document.getElementById('tracking-form-number');
    const trackingFormPhone = document.getElementById('tracking-form-phone');
    const trackingResult = document.getElementById('tracking-result');
  
    if (tabs.length && trackingFormNumber && trackingFormPhone && trackingResult) {
      tabs.forEach(tab => {
        tab.addEventListener('click', () => {
          tabs.forEach(t => t.classList.remove('active'));
          tab.classList.add('active');
          if (tab.dataset.tab === 'tracking-number') {
            trackingFormNumber.style.display = 'block';
            trackingFormPhone.style.display = 'none';
          } else {
            trackingFormNumber.style.display = 'none';
            trackingFormPhone.style.display = 'block';
          }
          trackingResult.innerHTML = '';
        });
      });
    }
  
    // =========================
    // 3. تتبع برقم التتبع (tracking-form-number)
    // =========================
    if (trackingFormNumber && trackingResult) {
      trackingFormNumber.addEventListener('submit', async (e) => {
        e.preventDefault();
        const numberInput = trackingFormNumber.querySelector('#tracking-number');
        const number = numberInput ? numberInput.value.trim() : '';
        if (loading) loading.style.display = 'block';
        trackingResult.innerHTML = '';
        try {
          const res = await fetch(`/api/orders/track/${encodeURIComponent(number)}/`);
          if (!res.ok) throw new Error('رقم التتبع غير موجود أو الحالة غير متاحة');
          const data = await res.json();
          trackingResult.innerHTML = `
            <p><strong>رقم التتبع:</strong> ${data.tracking_number || ''}</p>
            <p><strong>الحالة:</strong> ${data.status_display || ''}</p>
            <p><strong>من منطقة:</strong> ${data.from_area || ''}</p>
            <p><strong>إلى منطقة:</strong> ${data.to_area || ''}</p>
            <p><strong>تاريخ الإنشاء:</strong> ${data.created_at ? new Date(data.created_at).toLocaleString() : ''}</p>
          `;
        } catch (err) {
          trackingResult.innerHTML = `<p class="error">${err.message}</p>`;
        } finally {
          if (loading) loading.style.display = 'none';
        }
      });
    }
  
    // =========================
    // 4. تتبع برقم الهاتف (tracking-form-phone)
    // =========================
    if (trackingFormPhone && trackingResult) {
      trackingFormPhone.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phoneInput = trackingFormPhone.querySelector('#tracking-phone');
        const phone = phoneInput ? phoneInput.value.trim() : '';
        if (loading) loading.style.display = 'block';
        trackingResult.innerHTML = '';
        try {
          const res = await fetch(`/api/orders/track-by-phone/${encodeURIComponent(phone)}/`);
          if (!res.ok) throw new Error('لا توجد طلبات لهذا الرقم');
          const data = await res.json();
          if (!data || !Array.isArray(data) || data.length === 0) {
            trackingResult.innerHTML = `<p>لا توجد طلبات لهذا الرقم</p>`;
            return;
          }
          trackingResult.innerHTML = data.map(order => `
            <div class="order-item">
              <p><strong>رقم التتبع:</strong> ${order.tracking_number || ''}</p>
              <p><strong>الحالة:</strong> ${order.status_display || ''}</p>
              <p><strong>من منطقة:</strong> ${order.from_area || ''}</p>
              <p><strong>إلى منطقة:</strong> ${order.to_area || ''}</p>
              <p><strong>تاريخ الإنشاء:</strong> ${order.created_at ? new Date(order.created_at).toLocaleString() : ''}</p>
            </div>
          `).join('');
        } catch (err) {
          trackingResult.innerHTML = `<p class="error">${err.message}</p>`;
        } finally {
          if (loading) loading.style.display = 'none';
        }
      });
    }
  });
  
  // Orascom Go - script.js (Fixed Version)
document.addEventListener('DOMContentLoaded', () => {
    // =========================
    // 1. الطلب بدون تسجيل (guest-order-form)
    // =========================
    const guestForm = document.getElementById('guest-order-form');
    const submitBtn = guestForm ? document.getElementById('submit-guest-order') : null;
    const spinner = submitBtn ? submitBtn.querySelector('.spinner') : null;
    const loading = document.getElementById('loading');
  
    if (guestForm && submitBtn && spinner) {
      guestForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        submitBtn.disabled = true;
        spinner.style.display = 'inline-block';
        if (loading) loading.style.display = 'block';
  
        const orderData = {
          customer_name: guestForm.querySelector('#order-name')?.value || '',
          customer_phone: guestForm.querySelector('#order-phone')?.value || '',
          from_area: guestForm.querySelector('#order-from')?.value || '',
          to_area: guestForm.querySelector('#order-to')?.value || '',
          pickup_address: guestForm.querySelector('#order-address')?.value || '',
          delivery_address: guestForm.querySelector('#order-address')?.value || '',
          weight: parseFloat(guestForm.querySelector('#order-weight')?.value) || 0,
          service_type: guestForm.querySelector('#order-service-type')?.value || '',
          notes: guestForm.querySelector('#order-notes')?.value || '',
          payment_method: guestForm.querySelector('input[name="payment"]:checked')?.value || ''
        };
  
        try {
          const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
          const response = await fetch('/api/orders/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...(csrf ? { 'X-CSRFToken': csrf.value } : {})
            },
            body: JSON.stringify(orderData)
          });
          const result = await response.json();
          if (response.ok) {
            alert(`تم إنشاء الطلب بنجاح!\nرقم التتبع: ${result.tracking_number || ''}`);
            guestForm.reset();
          } else {
            alert('حصل خطأ: ' + (result.detail || JSON.stringify(result)));
          }
        } catch (err) {
          alert('فشل الاتصال');
        } finally {
          submitBtn.disabled = false;
          spinner.style.display = 'none';
          if (loading) loading.style.display = 'none';
        }
      });
    }
  
    // =========================
    // 2. التابات للتبديل بين تتبع برقم التتبع/الهاتف
    // =========================
    const tabs = document.querySelectorAll('.track-tab-btn');
    const trackingFormNumber = document.getElementById('tracking-form-number');
    const trackingFormPhone = document.getElementById('tracking-form-phone');
    const trackingResult = document.getElementById('tracking-result');
  
    if (tabs.length && trackingFormNumber && trackingFormPhone && trackingResult) {
      tabs.forEach(tab => {
        tab.addEventListener('click', () => {
          tabs.forEach(t => t.classList.remove('active'));
          tab.classList.add('active');
          if (tab.dataset.tab === 'tracking-number') {
            trackingFormNumber.style.display = 'block';
            trackingFormPhone.style.display = 'none';
          } else {
            trackingFormNumber.style.display = 'none';
            trackingFormPhone.style.display = 'block';
          }
          trackingResult.innerHTML = '';
        });
      });
    }
  
    // =========================
    // 3. تتبع برقم التتبع (tracking-form-number)
    // =========================
    if (trackingFormNumber && trackingResult) {
      trackingFormNumber.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log("🚀 Tracking form submitted!");
  
        const numberInput = trackingFormNumber.querySelector('#tracking-number');
        const number = numberInput ? numberInput.value.trim() : '';
        
        console.log("📌 Tracking Number Entered:", number);
  
        if (!number) {
          trackingResult.innerHTML = `<p class="error">⚠️ من فضلك أدخل رقم التتبع</p>`;
          return;
        }
  
        trackingResult.innerHTML = `<p style="text-align: center; color: #7f8c8d;">جاري البحث...</p>`;
  
        try {
          const res = await fetch(`/api/orders/track/${encodeURIComponent(number)}/`);
          
          if (!res.ok) {
            throw new Error('رقم التتبع غير موجود');
          }
  
          const data = await res.json();
          console.log("✅ Response data:", data);
  
          // بناء التايم لاين
          const steps = [
            { key: "pending", label: "قيد الانتظار" },
            { key: "confirmed", label: "تم التأكيد" },
            { key: "picked_up", label: "تم الاستلام" },
            { key: "in_transit", label: "في الطريق" },
            { key: "out_for_delivery", label: "خرج للتسليم" },
            { key: "delivered", label: "تم التسليم" }
          ];
  
          let activeIndex = steps.findIndex(s => s.key === data.status);
          if (activeIndex === -1) activeIndex = 0;
  
          trackingResult.innerHTML = `
            <div class="tracking-card">
              <h3>🔍 حالة الشحنة</h3>
              <div class="tracking-details">
                <p><strong>رقم التتبع:</strong> <span>${data.tracking_number || ''}</span></p>
                <p><strong>الحالة الحالية:</strong> <span style="color: #27ae60; font-weight: bold;">${data.status_display || ''}</span></p>
                <p><strong>من:</strong> <span>${data.from_area || ''}</span></p>
                <p><strong>إلى:</strong> <span>${data.to_area || ''}</span></p>
                <p><strong>تاريخ الإنشاء:</strong> <span>${data.created_at ? new Date(data.created_at).toLocaleString('ar-EG') : ''}</span></p>
              </div>
              <div class="timeline-container">
                <div class="timeline-title">📦 مسار الشحنة</div>
                <div class="timeline">
                  ${steps.map((step, index) => `
                    <div class="step ${index <= activeIndex ? 'active' : ''}">
                      <div class="dot"></div>
                      <span>${step.label}</span>
                    </div>
                  `).join('')}
                </div>
              </div>
            </div>
          `;
        } catch (err) {
          console.error("❌ Error:", err);
          trackingResult.innerHTML = `<p class="error">❌ ${err.message}</p>`;
        }
      });
    }
  
    // =========================
    // 4. تتبع برقم الهاتف (tracking-form-phone)
    // =========================
    if (trackingFormPhone && trackingResult) {
      trackingFormPhone.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log("🚀 Phone tracking form submitted!");
  
        const phoneInput = trackingFormPhone.querySelector('#tracking-phone');
        const phone = phoneInput ? phoneInput.value.trim() : '';
        
        console.log("📌 Phone Number Entered:", phone);
  
        if (!phone) {
          trackingResult.innerHTML = `<p class="error">⚠️ من فضلك أدخل رقم الهاتف</p>`;
          return;
        }
  
        trackingResult.innerHTML = `<p style="text-align: center; color: #7f8c8d;">جاري البحث...</p>`;
  
        try {
          const res = await fetch(`/api/orders/track-by-phone/${encodeURIComponent(phone)}/`);
          
          if (!res.ok) {
            throw new Error('لا توجد طلبات لهذا الرقم');
          }
  
          const data = await res.json();
          console.log("✅ Response data:", data);
  
          if (!data || !Array.isArray(data) || data.length === 0) {
            trackingResult.innerHTML = `<p style="text-align: center; color: #7f8c8d;">لا توجد طلبات لهذا الرقم</p>`;
            return;
          }
  
          trackingResult.innerHTML = data.map(order => {
            const steps = [
              { key: "pending", label: "قيد الانتظار" },
              { key: "confirmed", label: "تم التأكيد" },
              { key: "picked_up", label: "تم الاستلام" },
              { key: "in_transit", label: "في الطريق" },
              { key: "out_for_delivery", label: "خرج للتسليم" },
              { key: "delivered", label: "تم التسليم" }
            ];
  
            let activeIndex = steps.findIndex(s => s.key === order.status);
            if (activeIndex === -1) activeIndex = 0;
  
            return `
              <div class="tracking-card">
                <h3>📦 طلب رقم ${order.tracking_number}</h3>
                <div class="tracking-details">
                  <p><strong>رقم التتبع:</strong> <span>${order.tracking_number || ''}</span></p>
                  <p><strong>الحالة الحالية:</strong> <span style="color: #27ae60; font-weight: bold;">${order.status_display || ''}</span></p>
                  <p><strong>من:</strong> <span>${order.from_area || ''}</span></p>
                  <p><strong>إلى:</strong> <span>${order.to_area || ''}</span></p>
                  <p><strong>تاريخ الإنشاء:</strong> <span>${order.created_at ? new Date(order.created_at).toLocaleString('ar-EG') : ''}</span></p>
                </div>
                <div class="timeline-container">
                  <div class="timeline-title">📦 مسار الشحنة</div>
                  <div class="timeline">
                    ${steps.map((step, index) => `
                      <div class="step ${index <= activeIndex ? 'active' : ''}">
                        <div class="dot"></div>
                        <span>${step.label}</span>
                      </div>
                    `).join('')}
                  </div>
                </div>
              </div>
            `;
          }).join('');
        } catch (err) {
          console.error("❌ Error:", err);
          trackingResult.innerHTML = `<p class="error">❌ ${err.message}</p>`;
        }
      });
    }
  });
  document.addEventListener('DOMContentLoaded', () => {
    console.log("✅ Register script loaded");

    // ===== Tab Switching =====
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length > 0) {
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                console.log("Tab clicked:", btn.dataset.tab);
                
                // إزالة active من جميع الأزرار والمحتويات
                tabButtons.forEach(b => b.classList.remove('active'));
                tabContents.forEach(tc => tc.classList.remove('active'));

                // إضافة active للزر المختار والمحتوى المقابل
                btn.classList.add('active');
                const tabId = btn.dataset.tab + '-tab';
                const tabContent = document.getElementById(tabId);
                if (tabContent) {
                    tabContent.classList.add('active');
                }
            });
        });
    }

    // ===== Driver Registration Form =====
    const driverForm = document.querySelector('#driver-tab .register-form');
    if (driverForm) {
        driverForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log("Driver form submitted");

            const formData = new FormData();
            
            // Get form values
            const inputs = driverForm.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                if (input.type === 'file') {
                    formData.append(input.name || 'license_image', input.files[0]);
                } else if (input.name === 'work_areas' || input.multiple) {
                    // Handle multiple select
                    const selectedOptions = Array.from(input.selectedOptions).map(opt => opt.value);
                    formData.append('work_areas', JSON.stringify(selectedOptions));
                } else if (input.value) {
                    formData.append(input.name || input.previousElementSibling?.textContent, input.value);
                }
            });

            // Add CSRF token if exists
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfToken) {
                formData.append('csrfmiddlewaretoken', csrfToken.value);
            }

            try {
                const response = await fetch('/api/register/driver/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken?.value || ''
                    }
                });

                const result = await response.json();
                console.log("Driver registration response:", result);

                if (response.ok) {
                    alert('✅ تم إرسال طلبك بنجاح! سنتواصل معك قريباً');
                    driverForm.reset();
                } else {
                    alert('❌ حدث خطأ: ' + (result.detail || result.message || 'حاول مجدداً'));
                }
            } catch (err) {
                console.error("Error:", err);
                alert('❌ فشل الاتصال بالخادم');
            }
        });
    }

    // ===== Merchant Registration Form =====
    const merchantForm = document.querySelector('#merchant-tab .register-form');
    if (merchantForm) {
        merchantForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log("Merchant form submitted");

            const formData = new FormData();
            
            // Get form values
            const inputs = merchantForm.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                if (input.value) {
                    formData.append(input.name || input.previousElementSibling?.textContent, input.value);
                }
            });

            // Add CSRF token if exists
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfToken) {
                formData.append('csrfmiddlewaretoken', csrfToken.value);
            }

            try {
                const response = await fetch('/api/register/merchant/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken?.value || ''
                    }
                });

                const result = await response.json();
                console.log("Merchant registration response:", result);

                if (response.ok) {
                    alert('✅ تم إرسال طلبك بنجاح! سنتواصل معك قريباً');
                    merchantForm.reset();
                } else {
                    alert('❌ حدث خطأ: ' + (result.detail || result.message || 'حاول مجدداً'));
                }
            } catch (err) {
                console.error("Error:", err);
                alert('❌ فشل الاتصال بالخادم');
            }
        });
    }
});
