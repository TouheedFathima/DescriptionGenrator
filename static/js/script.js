 function showCreateForm() {
        document.getElementById("createForm").style.display = "block";
        document.getElementById("passForm").style.display = "none";
        clearErrors();
        document.getElementById("chatbox").style.display = "none";
      }

      function showPassForm() {
        document.getElementById("createForm").style.display = "none";
        document.getElementById("passForm").style.display = "block";
        clearErrors();
        document.getElementById("chatbox").style.display = "none";
      }

      function showSalaryRange() {
        document.getElementById('salaryRange').style.display = 'block';
        document.getElementById("salaryFrom").focus();
      }

      function updatePackageValue() {
        const from = document.getElementById("salaryFrom").value;
        const to = document.getElementById("salaryTo").value;
        const packageInput = document.getElementById("package");

        if (from && to) {
          packageInput.value = `₹${from} - ₹${to}`;
        }
      }

      function clearErrors() {
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(el => el.textContent = '');
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => input.style.border = '');
      }

      function setError(field, message) {
        const errorEl = document.getElementById(`${field}-error`);
        const input = document.getElementById(field);
        if (errorEl && input) {
          errorEl.textContent = message;
          input.style.border = "2px solid red";
          input.scrollIntoView({ behavior: 'smooth', block: 'center' });
          input.focus();
        }
      }

      function validateFields() {
        const fields = [
          { id: "companyType", message: "Required: Please select a Recruiter Type" },
          { id: "postFor", message: "Required: Please select Post For" },
          { id: "postType", message: "Required: Please select a Post Type" },
          { id: "address", message: "Required: Please fill this field" },
          { id: "title", message: "Required: Please enter a Job Title" },
          { id: "package", message: "Required: Please enter a salary range" },
          { id: "lastDate", message: "Required: Please select a date" },
          { id: "vacancy", message: "Required: Vacancy must be a positive number", validate: value => parseInt(value) > 0 },
          { id: "skills", message: "Required: At least one skill is required", validate: value => value.split(',').map(s => s.trim()).filter(s => s).length > 0 },
          { id: "keywords", message: "Required: At least one keyword is required", validate: value => value.split(',').map(k => k.trim()).filter(k => k).length > 0 }
        ];

        clearErrors();

        for (const field of fields) {
          const input = document.getElementById(field.id);
          const value = input.value.trim();
          const isValid = field.validate ? field.validate(value) : value !== "";
          if (!isValid) {
            setError(field.id, field.message);
            return false;
          }
        }
        return true;
      }

      function generateDescription() {
        if (!validateFields()) {
          return;
        }

        const resultEl = document.getElementById("descriptionResult");
        resultEl.innerHTML = "<em>Generating description... please wait.</em>";
        resultEl.setAttribute("contenteditable", "false");
        document.getElementById("chatbox").style.display = "block";
        document.getElementById("downloadBtn").style.display = "none";
        document.getElementById("copyBtn").style.display = "none";

        const packageVal = document.getElementById("package").value;
        const salaryFrom = document.getElementById("salaryFrom").value;
        const salaryTo = document.getElementById("salaryTo").value;
        const salaryRange = salaryFrom && salaryTo ? `₹${salaryFrom} - ₹${salaryTo}` : packageVal;

        const eligibility = [];
        if (document.getElementById("freshers")?.checked) eligibility.push("Freshers");
        if (document.getElementById("experienced")?.checked) eligibility.push("Experienced");

        const benefitCheckboxes = document.querySelectorAll('div.form-group input[type="checkbox"]:checked');
        const benefits = Array.from(benefitCheckboxes)
          .filter(checkbox => checkbox.value && !["Freshers", "Experienced"].includes(checkbox.value))
          .map(cb => cb.value);

        const payload = {
          companyName: document.getElementById("companyName").value,
          companyType: document.getElementById("companyType").value,
          postFor: document.getElementById("postFor").value,
          postType: document.getElementById("postType").value,
          location: document.querySelector('input[name="location"]:checked').value,
          address: document.getElementById("address").value,
          title: document.getElementById("title").value,
          package: salaryRange,
          lastDate: document.getElementById("lastDate").value,
          vacancy: parseInt(document.getElementById("vacancy").value),
          skills: document.getElementById("skills").value,
          keywords: document.getElementById("keywords").value,
          description: document.getElementById('description').value,
          wordCount: document.getElementById("wordCount").value || null,
          eligibility: eligibility,
          benefits: benefits
        };

        fetch('http://127.0.0.1:4000/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        .then(response => {
          if (!response.ok) {
            return response.json().then(err => { throw err; });
          }
          return response.json();
        })
        .then(data => {
          resultEl.innerHTML = data.description;
          resultEl.setAttribute("contenteditable", "true");
          document.getElementById("chatbox").style.display = "block";
          document.getElementById("downloadBtn").style.display = "inline-block";
          document.getElementById("copyBtn").style.display = "inline-block";
        })
        .catch(error => {
          console.error('Error:', error);
          if (error.field) {
            setError(error.field, `Required: ${error.error}`);
          } else {
            resultEl.innerText = "Something went wrong!";
          }
          document.getElementById("chatbox").style.display = "block";
          document.getElementById("downloadBtn").style.display = "none";
          document.getElementById("copyBtn").style.display = "none";
        });
      }

      function validatePassFields() {
        const fields = [
          { id: "passCompanyName", message: "Required: Please enter a Company Name" },
          { id: "passOpportunityTitle", message: "Required: Please enter an Opportunity Title" },
          { id: "passOpportunityType", message: "Required: Please select an Opportunity Type" },
          { id: "passLocation", message: "Required: Please enter a Location" },
          { id: "passWorkMode", message: "Required: Please select a Work Mode" },
          { id: "passNumberOfOpenings", message: "Required: Number of Openings must be a positive number", validate: value => parseInt(value) > 0 },
          { id: "passLastDate", message: "Required: Please select a Last Date to Apply" },
          { id: "passSkillsRequired", message: "Required: At least one skill is required", validate: value => value.split(',').map(s => s.trim()).filter(s => s).length > 0 },
          { id: "passSalaryMin", message: "Required: Please enter a minimum salary", validate: value => value !== "" && parseInt(value) >= 0 },
          { id: "passSalaryMax", message: "Required: Please enter a maximum salary", validate: value => value !== "" && parseInt(value) >= 0 },
          { id: "passTimeCommitment", message: "Required: Please select a Time Commitment" },
          { id: "passRecruiterName", message: "Required: Please enter a Recruiter Name" },
          { id: "passPhoneNumber", message: "Required: Please enter a valid phone number (at least 10 digits)", validate: value => value.replace(/[^0-9]/g, '').length >= 10 },
          { id: "passEmailAddress", message: "Required: Please enter a valid email address", validate: value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) }
        ];

        clearErrors();

        for (const field of fields) {
          const input = document.getElementById(field.id);
          const value = input.value.trim();
          const isValid = field.validate ? field.validate(value) : value !== "";
          if (!isValid) {
            setError(field.id, field.message);
            return false;
          }
        }

        const salaryMin = parseInt(document.getElementById("passSalaryMin").value);
        const salaryMax = parseInt(document.getElementById("passSalaryMax").value);
        if (salaryMin > salaryMax) {
          setError("passSalaryMax", "Maximum salary must be greater than or equal to minimum salary");
          return false;
        }

        return true;
      }

      function passOpportunity() {
        if (!validatePassFields()) {
          return;
        }

        const resultEl = document.getElementById("descriptionResult");
        resultEl.innerHTML = "<em>Processing pass an opportunity... please wait.</em>";
        resultEl.setAttribute("contenteditable", "false");
        document.getElementById("chatbox").style.display = "block";
        document.getElementById("downloadBtn").style.display = "none";
        document.getElementById("copyBtn").style.display = "none";

        const salaryOptions = [];
        if (document.getElementById("passSalaryNegotiable").checked) salaryOptions.push("Negotiable");
        if (document.getElementById("passSalaryNotDisclose").checked) salaryOptions.push("Prefer Not to Disclose");
        if (document.getElementById("passSalaryNotSure").checked) salaryOptions.push("Not Sure");

        const payload = {
          companyName: document.getElementById("passCompanyName").value,
          opportunityTitle: document.getElementById("passOpportunityTitle").value,
          opportunityType: document.getElementById("passOpportunityType").value,
          location: document.getElementById("passLocation").value,
          workMode: document.getElementById("passWorkMode").value,
          numberOfOpenings: parseInt(document.getElementById("passNumberOfOpenings").value),
          lastDate: document.getElementById("passLastDate").value,
          educationRequirements: document.getElementById("passEducationRequirements").value,
          industryExpertise: document.getElementById("passIndustryExpertise").value,
          preferredExperience: document.getElementById("passPreferredExperience").value,
          skillsRequired: document.getElementById("passSkillsRequired").value,
          languagePreference: document.getElementById("passLanguagePreference").value,
          genderPreference: document.getElementById("passGenderPreference").value,
          salaryMin: parseInt(document.getElementById("passSalaryMin").value),
          salaryMax: parseInt(document.getElementById("passSalaryMax").value),
          salaryOptions: salaryOptions,
          timeCommitment: document.getElementById("passTimeCommitment").value,
          recruiterName: document.getElementById("passRecruiterName").value,
          phoneNumber: document.getElementById("passPhoneNumber").value,
          emailAddress: document.getElementById("passEmailAddress").value
        };

        fetch('http://127.0.0.1:4000/pass-opportunity', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        .then(response => {
          if (!response.ok) {
            return response.json().then(err => { throw err; });
          }
          return response.json();
        })
        .then(data => {
          resultEl.innerHTML = data.message;
          resultEl.setAttribute("contenteditable", "true");
          document.getElementById("chatbox").style.display = "block";
          document.getElementById("downloadBtn").style.display = "inline-block";
          document.getElementById("copyBtn").style.display = "inline-block";
        })
        .catch(error => {
          console.error('Error:', error);
          if (error.field) {
            setError(error.field, `Required: ${error.error}`);
          } else {
            resultEl.innerText = "Something went wrong!";
          }
          document.getElementById("chatbox").style.display = "block";
          document.getElementById("downloadBtn").style.display = "none";
          document.getElementById("copyBtn").style.display = "none";
        });
      }

      function generatePassWithAI() {
        if (!validatePassFields()) {
          return;
        }

        const resultEl = document.getElementById("descriptionResult");
        resultEl.innerHTML = "<em>Generating description with AI... please wait.</em>";
        resultEl.setAttribute("contenteditable", "false");
        document.getElementById("chatbox").style.display = "block";
        document.getElementById("downloadBtn").style.display = "none";
        document.getElementById("copyBtn").style.display = "none";

        const salaryOptions = [];
        if (document.getElementById("passSalaryNegotiable").checked) salaryOptions.push("Negotiable");
        if (document.getElementById("passSalaryNotDisclose").checked) salaryOptions.push("Prefer Not to Disclose");
        if (document.getElementById("passSalaryNotSure").checked) salaryOptions.push("Not Sure");

        const payload = {
          companyName: document.getElementById("passCompanyName").value,
          opportunityTitle: document.getElementById("passOpportunityTitle").value,
          opportunityType: document.getElementById("passOpportunityType").value,
          location: document.getElementById("passLocation").value,
          workMode: document.getElementById("passWorkMode").value,
          numberOfOpenings: parseInt(document.getElementById("passNumberOfOpenings").value),
          lastDate: document.getElementById("passLastDate").value,
          educationRequirements: document.getElementById("passEducationRequirements").value,
          industryExpertise: document.getElementById("passIndustryExpertise").value,
          preferredExperience: document.getElementById("passPreferredExperience").value,
          skillsRequired: document.getElementById("passSkillsRequired").value,
          languagePreference: document.getElementById("passLanguagePreference").value,
          genderPreference: document.getElementById("passGenderPreference").value,
          salaryMin: parseInt(document.getElementById("passSalaryMin").value),
          salaryMax: parseInt(document.getElementById("passSalaryMax").value),
          salaryOptions: salaryOptions,
          timeCommitment: document.getElementById("passTimeCommitment").value,
          recruiterName: document.getElementById("passRecruiterName").value,
          phoneNumber: document.getElementById("passPhoneNumber").value,
          emailAddress: document.getElementById("passEmailAddress").value
        };

        fetch('http://127.0.0.1:4000/pass-opportunity-generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        .then(response => {
          if (!response.ok) {
            return response.json().then(err => { throw err; });
          }
          return response.json();
        })
        .then(data => {
          resultEl.innerHTML = data.description;
          resultEl.setAttribute("contenteditable", "true");
          document.getElementById("chatbox").style.display = "block";
          document.getElementById("downloadBtn").style.display = "inline-block";
          document.getElementById("copyBtn").style.display = "inline-block";
        })
        .catch(error => {
          console.error('Error:', error);
          if (error.field) {
            setError(error.field, `Required: ${error.error}`);
          } else {
            resultEl.innerText = "Something went wrong!";
          }
          document.getElementById("chatbox").style.display = "block";
          document.getElementById("downloadBtn").style.display = "none";
          document.getElementById("copyBtn").style.display = "none";
        });
      }

      function formatText(command) {
        document.execCommand(command, false, null);
      }

      function copyToClipboard() {
        const content = document.getElementById('descriptionResult').innerHTML;
        const tempElem = document.createElement("div");
        tempElem.innerHTML = content;
        const text = tempElem.innerText;

        navigator.clipboard.writeText(text).then(() => {
          alert("Copied to clipboard!");
        });
      }

      function downloadDescription() {
        const content = document.getElementById('descriptionResult').innerHTML;
        const text = content.replace(/<[^>]+>/g, '');
        const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "description.txt";
        link.click();
      }

      function changeFont(fontName) {
        document.execCommand("fontName", false, fontName);
      }

      document.addEventListener("DOMContentLoaded", function() {
        const dateInput = document.getElementById("lastDate");
        const passDateInput = document.getElementById("passLastDate");

        if (dateInput && typeof dateInput.showPicker === 'function') {
          dateInput.addEventListener("focus", function () {
            this.showPicker();
          });
        }
        if (passDateInput && typeof passDateInput.showPicker === 'function') {
          passDateInput.addEventListener("focus", function () {
            this.showPicker();
          });
        }
      });