import os
import json
import requests
import pandas as pd
import streamlit as st
from fpdf import FPDF
from src.validator import validate_vin

st.set_page_config(
    page_title="Vehicle Risk Assessment System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("<h1 style='text-align: center;'>VEHICLE RISK ASSESSMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("---")

DATABASE_FILE_PATH = os.path.join("data", "demo_vehicle_history.json")

if os.path.exists(DATABASE_FILE_PATH):
    with open(DATABASE_FILE_PATH, "r", encoding="utf-16") as opened_json_file:
        records = json.load(opened_json_file)
    vehicle_dataframe = pd.DataFrame(records)
    
    if "source_label" in vehicle_dataframe.columns:
        vehicle_dataframe["source_label"] = "Demo dataset"
        
    total_car_records = len(vehicle_dataframe)
    damaged_cars = int(vehicle_dataframe["salvage_flag_demo"].sum())
    damaged_car_percentage = (damaged_cars / total_car_records) * 100 if total_car_records > 0 else 0.0
    check_imported_cars = len(vehicle_dataframe[(vehicle_dataframe["imported_from_country_demo"] != "US") & (vehicle_dataframe["salvage_flag_demo"] == 0)])
    
    st.markdown("<h3 style='text-align: center;'>CAR RISK PROFILES</h3>", unsafe_allow_html=True)
    metric_column_left, metric_column_center, metric_column_right = st.columns(3)
    metric_column_left.metric("Processed Vehicle Records", f"{total_car_records} Vehicles")
    metric_column_center.metric("Damaged Cars Rate", f"{damaged_car_percentage:.1f}%")
    metric_column_right.metric("Imported Vehicles needing verification", f"{check_imported_cars} Units")
    
    st.markdown("---")
    
    st.markdown("<h3 style='text-align: center;'>SAMPLED VEHICLE DATASET REGISTRY</h3>", unsafe_allow_html=True)
    display_config = {
        "vin": st.column_config.TextColumn("Vehicle Identification Number (VIN)", alignment="center"),
        "data_type": st.column_config.TextColumn("Data Type", alignment="center"),
        "source_label": st.column_config.TextColumn("Data Source", alignment="center"),
        "imported_from_country_demo": st.column_config.TextColumn("Imported Country", alignment="center"),
        "auction_price_demo": st.column_config.NumberColumn("Auction Price", alignment="center"),
        "salvage_flag_demo": st.column_config.TextColumn("Damaged Cars", alignment="center"),
        "accident_count_demo": st.column_config.NumberColumn("Recorded Accidents", alignment="center")
    }
    st.dataframe(
        vehicle_dataframe, 
        use_container_width=True, 
        hide_index=True,
        column_config=display_config,
        height=400
    )
    
    st.markdown("---")
    
    st.markdown("<h3 style='text-align: center;'>VIN VALIDATION REPORT CONSOLE</h3>", unsafe_allow_html=True)
    user_vin = st.text_input(
        "ENTER A 17-CHARACTER VIN TO GENERATE THE RISK REPORT:", 
        placeholder="e.g., 1HKRW1H50KRE00030",
        max_chars=17
    ).strip().upper()
    
    if user_vin:
        st.markdown(f" Assessment Summary for VIN: {user_vin}")
        
        is_compliant = validate_vin(user_vin)
        if not is_compliant:
            st.error(
                f"VIN Validation Failure: The sequence {user_vin} does not comply with structural parameters. "
                "Reason: A valid VIN must be exactly 17 characters long, exclude illegal letters (I, O, Q), "
                "and pass the mathematical modulus-11 weight validation formula on the 9th position check-digit."
            )
            vin_validation_passed = False
        else:
            st.success(
                "VIN Validation Success: Sequence matches length constraints, excludes illegal characters (I, O, Q), "
                "and satisfies the official mathematical modulus-11 check-digit verification on character position 9."
            )
            vin_validation_passed = True

        st.markdown(" How the Code Verification Rules Work")
        st.write(
            "Every official car code has a secret check-letter or check-number built right into its 9th position. "
            "Our system runs a math formula that adds up the letters and positions to see if they match this check-number. "
            "This makes sure the serial number you typed is real and prevents typos or fake entries."
        )

        st.markdown(" System Storage Disclaimers & Limitations")
        st.info(
            "IMPORTANT NOTICE: This app is an educational school project tool and is not a real commercial history business. "
            "Things like full background crash history, old insurance logs, and master market price data are protected behind "
            "expensive, paid commercial business accounts. Because there are no free public ways to look up this information on "
            "the web, we use a small file of fake sample records to test how the system works."
        )
        st.markdown("---")
            
        api_success = False
        make, model, year = "Not Available", "Not Available", "Not Available"
        manufacturer, body_class, vehicle_type = "Not Available", "Not Available", "Not Available"
        recalls_list = []
        
        try:
            vehicle_database_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{user_vin}?format=json"
            response = requests.get(vehicle_database_url, timeout=10)
            if response.status_code == 200:
                results = response.json().get("Results", [])
                data_dict = {item["Variable"]: item["Value"] for item in results if item["Value"]}
                make = data_dict.get("Make", "Not Available")
                model = data_dict.get("Model", "Not Available")
                year = data_dict.get("Model Year", "Not Available")
                manufacturer = data_dict.get("Manufacturer Name", "Not Available")
                body_class = data_dict.get("Body Class", "Not Available")
                vehicle_type = data_dict.get("Vehicle Type", "Not Available")
                api_success = True
        except Exception as connection_error_exception:
            st.error(f"NHTSA vPIC API Connection Fault: {str(connection_error_exception)}")

        if api_success and make != "Not Available" and model != "Not Available" and year != "Not Available":
            try:
                recall_url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={make}&model={model}&modelYear={year}"
                recall_api_response = requests.get(recall_url, timeout=10)
                if recall_api_response.status_code == 200:
                    recalls_list = recall_api_response.json().get("results", [])
            except Exception:
                pass

        local_record = vehicle_dataframe[vehicle_dataframe["vin"] == user_vin]
        has_local_history = not local_record.empty
        
        specification_column, history_column = st.columns(2)
        
        with specification_column:
            st.markdown("Technical Specifications")
            st.write(f"Car Brand: {make} (Source: Live Official API)")
            st.write(f"Model: {model} (Source: Live Official API)")
            st.write(f"Model Year: {year} (Source: Live Official API)")
            st.write(f"Manufacturer: {manufacturer} (Source: Live Official API)")
            st.write(f"Body Class: {body_class} (Source: Live Official API)")
            st.write(f"Vehicle Type: {vehicle_type} (Source: Live Official API)")
            
            st.markdown("Manufacturer Safety Recalls")
            if len(recalls_list) > 0:
                st.warning(f"Active Campaigns Detected: {len(recalls_list)}")
                
                displayed_summaries = []
                displayed_count = 0
                for recall_record in recalls_list:
                    current_summary = recall_record.get('summary', 'No description provided.')
                    if current_summary not in displayed_summaries:
                        displayed_summaries.append(current_summary)
                        
                        st.markdown(f"Safety Description Code: {recall_record.get('campNo', 'None')}")
                        st.markdown(f"Affected Car Part:{recall_record.get('component', 'None')}")
                        st.markdown(f"Problem Description: {current_summary}")
                    
                        displayed_count += 1
                        if displayed_count >= 3:
                            break
            else:
                st.info("No active safety recall records identified via NHTSA recalls API.")
                
        with history_column:
            st.markdown("Internal History Registry Record")
            if has_local_history:
                matched_vehicle_row = local_record.iloc[0]
                st.write(f"Imported Country: {matched_vehicle_row.get('imported_from_country_demo')} (Source: Demo dataset)")
                st.write(f"Auction Price: ${matched_vehicle_row.get('auction_price_demo')} (Source: Demo dataset)")
                
                salvage_status = "TRUE (Total Loss Status)" if matched_vehicle_row.get('salvage_flag_demo') == 1 else "FALSE (Clear Status)"
                st.write(f"Damaged Cars Status: {salvage_status} (Source: Demo dataset)")
                st.write(f"Recorded Accidents: {matched_vehicle_row.get('accident_count_demo')} (Source: Demo dataset)")
                
                salvage_trigger = matched_vehicle_row.get('salvage_flag_demo') == 1
                accident_trigger = int(matched_vehicle_row.get('accident_count_demo', 0))
            else:
                st.info("No matching historical metadata located in the demo dataset file.")
                salvage_trigger = False
                accident_trigger = 0

            st.markdown("Operational Risk Index Assessment")
            risk_points = 0
            reasons = []
            
            if not vin_validation_passed:
                risk_points += 3
                reasons.append("VIN sequence failed geometric format constraints.")
            if len(recalls_list) > 3:
                risk_points += 2
                reasons.append("Elevated factory safety recall density.")
            elif len(recalls_list) > 0:
                risk_points += 1
                reasons.append("Active factory recall conditions observed.")
            if salvage_trigger:
                risk_points += 3
                reasons.append("Internal database logs record historical structural total loss.")
            if accident_trigger > 1:
                risk_points += 2
                reasons.append("Chronic accident occurrence logged in historical registry.")
            elif accident_trigger == 1:
                risk_points += 1
                reasons.append("Single baseline historical accident occurrence logged.")

            final_alert_level = "High Risk" if risk_points >= 4 else "Warning" if risk_points >= 2 else "Low Risk"

            if risk_points >= 4:
                st.error(f"Risk Rating Score: {risk_points} / HIGH COMPLIANCE THREAT")
            elif risk_points >= 2:
                st.warning(f"Risk Rating Score: {risk_points} / ELEVATED COMPLIANCE WARNING")
            else:
                st.success(f"Risk Rating Score: {risk_points} / LOW REGULATORY RISK")
                
            for reason in reasons:
                st.markdown(f"- {reason}")
                
            found_in_file = "Yes" if has_local_history else "No"
            built_country = str(matched_vehicle_row.get('imported_from_country_demo', 'Not Available')) if has_local_history else 'Not Available'
            listed_val = f"${matched_vehicle_row.get('auction_price_demo', '0')}" if has_local_history else '$0'
            severe_loss = "Yes" if (has_local_history and matched_vehicle_row.get('salvage_flag_demo') == 1) else "No"
            num_crashes = str(matched_vehicle_row.get('accident_count_demo', '0')) if has_local_history else '0'
            text_rule = "Passed" if vin_validation_passed else "Failed"
            current_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

            receipt_text = f"""--------------------------------------------------
                               VEHICLE DATA CHECK RECEIPT             
--------------------------------------------------
Checked Vehicle Serial Number (VIN): {user_vin}
Time of Check: {current_time}
--------------------------------------------------

1. WHAT IS RECORDED IN OUR LOCAL REGISTRY FILE
- Found in Dataset: {found_in_file}
- Country of Origin: {built_country}
- Estimated Valuation: {listed_val}
- Prior Severe Damage Record: {severe_loss}
- Total Recorded Crashes: {num_crashes}

2. WHAT THE LIVE MANUFACTURER DATABASES SAY
- Real Vehicle Description: {f"{make} {model}"if make != "Not Available" else "Not Available"}
-Manufacturing Year: {year}
- Active Manufacturer Safety Repairs Needed: {len(recalls_list)}

3. SYSTEM VERIFICATION RESULTS
- Serial Number Structure Match: {text_rule}
- Overall System Safety Decision: {final_alert_level}
--------------------------------------------------
Thank you for running this vehicle safety check!
--------------------------------------------------"""
            pdf = FPDF()
            pdf .add_page()
            pdf.set_font("Courier", size=10) 
            
            for line in receipt_text.split('\n'):
                pdf.cell(0, 5, txt=line, ln=True)
                
            pdf_bytes = pdf.output(dest='S').encode('latin1')

            st.markdown("---")
            st.markdown("PDF AND TXT REPORT EXPORT PANEL")

            export_button_left, export_button_right = st.columns(2)
            
            export_button_left.download_button(
                label="Export Report to TXT",
                data=receipt_text,
                file_name=f"Data_Check_Receipt_{user_vin}.txt",
                mime="text/plain"
            )
            
            export_button_right.download_button(
                label="Export Report to PDF",
                data=pdf_bytes,
                file_name=f"Data_Check_Receipt_{user_vin}.pdf",
                mime="application/pdf"
            )

        

    st.markdown("<h3 style='text-align: center;'>SYSTEM GLOSSARY AND OPERATION GUIDE</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>This documentation explains the parameters tracked within the system and provides guidance on running independent compliance checks.</p>", unsafe_allow_html=True)
    
    st.markdown(" 1. Data Field Definitions")
    st.markdown(
        """
        | Data Field Name | Definition and Purpose | Practical Example |
        | :--- | :--- | :--- |
        | Vehicle Identification Number (VIN) | The unique 17-character sequence assigned to a vehicle by its manufacturer. | 1FA6P8CF0LRE00003 |
        | Data Type | System categorization tracker showing if a record is real production or mock demonstration data. | demo |
        | Data Source | Identifies the database origin or provider from which the car's record was acquired. | Demo dataset |
        | Imported Country | The origin country where the unit was built or registered prior to wholesale. | Germany |
        | Auction Price | The market transaction valuation recorded during the asset wholesale processing. | 16500 |
        | Damaged Cars | Legal designation tracker confirming severe structural impact history or total-loss write-off. | True or False |
        | Recorded Accidents | Continuous numerical tracker summing total historical collision occurrences. | 2 |
        """
    )
    
    st.markdown(" 2. Summary Metric Explanations")
    st.markdown(
        """
        * Processed Vehicle Records: The aggregate volume of entries successfully loaded from the dataset framework.
        * Damaged Cars Rate: The calculated ratio dividing salvage units by total inventory records to monitor baseline fleet health.
        * Imported Vehicles needing verification: Tracks vehicles brought in from foreign countries that don't have recorded damage flags, prompting a manual double-check for unrecorded history.
        """
    )
else:
    st.error("Initialization failure: Database file data/demo_vehicle_history.json not resolved.")