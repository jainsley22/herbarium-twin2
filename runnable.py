
import ai_vision
import streamlit as st
import os
from PIL import Image, ImageOps

import db
import qr_tools
from pathlib import Path


# -----------------------------
# Initialization
# -----------------------------

db.db_init()

st.set_page_config(
    page_title="Herbarium Twin 2",
    layout="wide",
)

st.title("Herbarium Twin 2")
st.write("AI-assisted herbarium inventory system")


# -----------------------------
# Tabs
# -----------------------------

tab1, tab2 = st.tabs(
    [
        ":package: New Inventory",
        ":mag_right: Existing Collection",
    ]
)


# ==================================================
# TAB 1: NEW INVENTORY
# ==================================================

with tab1:
    st.header("Create Herbarium Unit Record")

    # -----------------------------
    # Basic information
    # -----------------------------

    unit_id = st.text_input(
        "Unit ID",
        value=db.get_next_unit_id(),
    )

    location = st.text_input(
        "Current Location *",
        placeholder="Example: Room 204 Shelf B",
    )

    inventor = st.text_input("Inventoried By")

    # -----------------------------
    # Image upload
    # -----------------------------

    st.subheader("Upload Images")

    uploaded_files = st.file_uploader(
        "Upload herbarium unit photos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )

    image_paths = []

    if uploaded_files:
        os.makedirs("captured_images", exist_ok=True)

        for i, file in enumerate(uploaded_files):
            img = Image.open(file)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            temp_path = os.path.join(
                "captured_images",
                f"{unit_id}_{i}.jpg",
            )

            img.save(temp_path)
            image_paths.append(temp_path)

            st.image(
                img,
                caption=file.name,
                width=250,
            )

        # -----------------------------
        # AI analysis
        # -----------------------------

        if (
            "ai_results" not in st.session_state
            or st.session_state.get("last_unit") != unit_id
        ):
            with st.spinner(":robot_face: AI analyzing herbarium images..."):
                try:
                    st.session_state.ai_results = ai_vision.analyze_box_images(image_paths)
                    st.session_state.last_unit = unit_id
                except Exception as e:
                    st.error(f"AI failed: {e}")

    ai = st.session_state.get("ai_results", {})

    # -----------------------------
    # AI-generated fields
    # -----------------------------

    st.subheader("AI Generated Metadata")

    collection_area = st.text_input(
        "Collection Area",
        ai.get("collection_area", ""),
    )

    material_type = st.text_input(
        "Material Type",
        ai.get("material_type", ""),
    )

    packet_count = st.text_input(
        "Estimated Packet Count",
        ai.get("estimated_packet_count", ""),
    )

    taxonomic = st.text_area(
        "Taxonomic Clues",
        ai.get("taxonomic_clues", ""),
    )

    geographic = st.text_area(
        "Geographic Clues",
        ai.get("geographic_clues", ""),
    )

    collector = st.text_area(
        "Collector Clues",
        ai.get("collector_clues", ""),
    )

    condition = st.text_input(
        "Condition",
        ai.get("condition", ""),
    )

    processing = st.text_input(
        "Processing Status",
        ai.get("processing_status", ""),
    )

    priority = st.text_input(
        "Priority",
        ai.get("priority", ""),
    )

    # -----------------------------
    # Human input
    # -----------------------------

    human_notes = st.text_area("Human Notes")

    ai_summary = st.text_area(
        "AI Summary",
        ai.get("ai_summary", ""),
    )

    confidence = st.text_input(
        "AI Confidence Notes",
        ai.get("ai_confidence_notes", ""),
    )

    # -----------------------------
    # Save
    # -----------------------------

    if st.button(":floppy_disk: Save Herbarium Unit"):
        if not location:
            st.error("Current location is required.")
        elif db.unit_id_exists(unit_id):
            st.error("Unit ID already exists.")
        else:
            record = {
                "unit_id": unit_id,
                "current_location": location,
                "collection_area": collection_area,
                "material_type": material_type,
                "estimated_packet_count": packet_count,
                "taxonomic_clues": taxonomic,
                "geographic_clues": geographic,
                "collector_clues": collector,
                "condition": condition,
                "processing_status": processing,
                "priority": priority,
                "human_notes": human_notes,
                "ai_summary": ai_summary,
                "ai_confidence_notes": confidence,
                "image_paths": ",".join(image_paths),
                "inventoried_by": inventor,
            }

            db.save_box(record)
            qr_path = qr_tools.generate_box_qr(unit_id, location)
            st.success(f"Saved {unit_id}")
            st.image(qr_path, caption="Unit QR Code")


# ==================================================
# TAB 2: EXISTING COLLECTION
# ==================================================

with tab2:
    st.header("Inventory Database")

    boxes = db.get_all_boxes()

    # ==================================
    # EXPORT COMPLETE DATABASE TO CSV
    # ==================================

    st.subheader("Export Collection Database")

    csv_data = db.export_boxes_csv()

    st.download_button(
        label="Download Complete Collection as CSV",
        data=csv_data,
        file_name="herbarium_collection_export.csv",
        mime="text/csv",
        key="download_complete_collection_csv"
    )

    st.divider()

    if not boxes:
        st.info("No units inventoried yet.")

    else:
        for unit in boxes:
            unit_id = unit[0]

            with st.expander(f":package: {unit_id}"):

                st.write("Location:", unit[1])
                st.write("Material:", unit[3])
                st.write("Summary:", unit[12])

                # Display associated images
                if unit[14]:

                    image_paths = unit[14].split(",")

                    columns = st.columns(3)

                    for i, image_path in enumerate(image_paths):

                        # Clean image path
                        image_path = image_path.strip().replace("\\", "/")

                        # Extract filename
                        image_filename = Path(image_path).name

                        # Find image inside captured_images folder
                        full_path = (
                            Path(__file__).resolve().parent
                            / "captured_images"
                            / image_filename
                        )

                        if full_path.exists():

                            with Image.open(full_path) as img:

                                # Correct image orientation
                                img = ImageOps.exif_transpose(img)

                                # Display image
                                with columns[i % 3]:
                                    st.image(
                                        img,
                                        use_container_width=True
                                    )

                        else:
                            st.warning(
                                f"Image not found: {image_filename}"
                            )

                # ==================================
                # QR CODE DOWNLOAD
                # ==================================

                st.divider()

                st.subheader("Download Unit QR Code")

                qr_folder = (
                    Path(__file__).resolve().parent
                    / "qr_codes"
                )

                qr_path = qr_folder / f"{unit_id}.png"

                if qr_path.exists():

                    with open(qr_path, "rb") as file:

                        st.download_button(
                            label="Download QR Code",
                            data=file.read(),
                            file_name=f"{unit_id}_QR.png",
                            mime="image/png",
                            key=f"qr_download_{unit_id}"
                        )

                    st.image(
                        str(qr_path),
                        caption=f"QR Code: {unit_id}",
                        width=150
                    )

                else:
                    st.warning(
                        f"QR code not found for {unit_id}."
                    )

                # ==================================
                # JSON EXPORT
                # ==================================

                st.divider()

                st.subheader("Export Collection Record")

                json_path = db.export_box_json(unit_id)

                if json_path:

                    with open(json_path, "rb") as file:

                        st.download_button(
                            label="Download Complete JSON Record",
                            data=file.read(),
                            file_name=f"{unit_id}.json",
                            mime="application/json",
                            key=f"json_{unit_id}"
                        )
