Decode::RETURN Decode::ReadByte(FIT_UINT8 data)
{
    if ((fileBytesLeft > 0) && (skipHeader == FIT_FALSE))
    {
        crc = CRC::Get16(crc, data);

        fileBytesLeft--;

        if (fileBytesLeft == 1) // CRC low byte.
        {
            if (state != STATE_RECORD)
            {
                std::ostringstream message;
                message << "FIT decode error: Decoder not in correct state after last data byte in file. Check message definitions. Error at byte: " << currentByteOffset;
                throw(RuntimeException(message.str()));
            }

            return RETURN_CONTINUE; // Next byte.
        }

        if (fileBytesLeft == 0) // CRC high byte.
        {
            if (crc != 0)
            {
                std::ostringstream message;
                message << "FIT decode error: File CRC failed. Error at byte: " << currentByteOffset;
                throw(RuntimeException(message.str()));
            }

            return RETURN_END_OF_FILE;
        }
    }

    switch (state) {
        case STATE_FILE_HDR:
            switch (fileHdrOffset++)
            {
                case 0:
                    if( data < FIT_HEADER_SIZE_NO_CRC )
                    {
                        std::ostringstream message;
                        message << "FIT decode error: File header size invalid.  File is not FIT. Error at byte : " << currentByteOffset;
                        headerException = message.str();
                    }
                    else
                    {
                        fileHdrSize = data;
                        fileBytesLeft = fileHdrSize + 2;
                    }
                    break;
                case 1:
                    if ((data & FIT_PROTOCOL_VERSION_MAJOR_MASK) > (FIT_PROTOCOL_VERSION_MAJOR << FIT_PROTOCOL_VERSION_MAJOR_SHIFT))
                    {
                        std::ostringstream message;
                        message << "FIT decode error: Protocol version " << (data & FIT_PROTOCOL_VERSION_MAJOR_MASK) << FIT_PROTOCOL_VERSION_MAJOR_SHIFT << "." << (data & FIT_PROTOCOL_VERSION_MINOR_MASK) << " not supported.  Must be " << FIT_PROTOCOL_VERSION_MAJOR << ".15 or earlier.";
                        headerException = message.str();
                    }
                    break;
                case 4:
                    fileDataSize = data & 0xFF;
                    break;
                case 5:
                    fileDataSize |= (FIT_UINT32) (data & 0xFF) << 8;
                    break;
                case 6:
                    fileDataSize |= (FIT_UINT32) (data & 0xFF) << 16;
                    break;
                case 7:
                    fileDataSize |= (FIT_UINT32) (data & 0xFF) << 24;
                    if ( (fileDataSize == 0) && (invalidDataSize == FIT_FALSE) )
                    {
                        invalidDataSize = FIT_TRUE;
                        std::ostringstream message;
                        message << "FIT decode error: File Size is 0. Error at byte : " << currentByteOffset;
                        headerException = message.str();
                    }
                    break;
                case 8:
                    if (data != '.')
                    {
                        std::ostringstream message;
                        message << "FIT decode error: File header signature mismatch.  File is not FIT. Error at byte : " << currentByteOffset;
                        headerException = message.str();
                    }
                    break;
                case 9:
                    if (data != 'F')
                    {
                        std::ostringstream message;
                        message << "FIT decode error: File header signature mismatch.  File is not FIT. Error at byte : " << currentByteOffset;
                        headerException = message.str();
                    }
                    break;
                case 10:
                    if (data != 'I')
                    {
                        std::ostringstream message;
                        message << "FIT decode error: File header signature mismatch.  File is not FIT. Error at byte : " << currentByteOffset;
                        headerException = message.str();
                    }
                    break;
                case 11:
                    if (data != 'T')
                    {
                        std::ostringstream message;
                        message << "FIT decode error: File header signature mismatch.  File is not FIT. Error at byte : " << currentByteOffset;
                        headerException = message.str();
                    }

                    if (headerException != "")
                    {
                        throw(RuntimeException(headerException));
                    }
                    break;
                default:
                    break;
            }

            if (fileHdrOffset == fileHdrSize)
            {
                fileBytesLeft = fileDataSize + 2; // include crc
                state = STATE_RECORD;

                // We don't care about the CRC when the file size is invalid
                if (invalidDataSize)
                {
                    skipHeader = FIT_TRUE;
                }
            }
            break;

        case STATE_RECORD:
            fieldIndex = 0;
            fieldBytesLeft = 0;

            if (fileBytesLeft > 1) {
                if ((data & FIT_HDR_TIME_REC_BIT) != 0) {
                    Field timestampField = Field(Profile::MESG_RECORD, Profile::RECORD_MESG_TIMESTAMP);
                    FIT_UINT8 timeOffset = data & FIT_HDR_TIME_OFFSET_MASK;

                    timestamp += (timeOffset - lastTimeOffset) & FIT_HDR_TIME_OFFSET_MASK;
                    lastTimeOffset = timeOffset;
                    timestampField.SetUINT32Value(timestamp);

                    localMesgIndex = (data & FIT_HDR_TIME_TYPE_MASK) >> FIT_HDR_TIME_TYPE_SHIFT;
                    MesgDefinition& localDef = localMesgDefs[localMesgIndex];

                    if (localDef.GetNum() == FIT_MESG_NUM_INVALID)
                    {
                        std::ostringstream message;
                        message << "FIT decode error: Missing FIT message definition for local message number " << ((int)localMesgIndex) << ". Error at byte: " << currentByteOffset;
                        throw(RuntimeException(message.str()));
                    }

                    mesg = Mesg(localDef.GetNum());
                    mesg.SetLocalNum(localMesgIndex);
                    mesg.AddField(timestampField);

                    if (localDef.GetFields().size() == 0)
                        return RETURN_MESG;

                    state = STATE_FIELD_DATA;
                }
                else
                {
                    localMesgIndex = data & FIT_HDR_TYPE_MASK;

                    if ((data & FIT_HDR_TYPE_DEF_BIT) != 0)
                    {
                        hasDevData = ((data & FIT_HDR_DEV_FIELD_BIT) != 0);
                        state = STATE_RESERVED1;
                    }
                    else
                    {
                        MesgDefinition& localDef = localMesgDefs[localMesgIndex];
                        if (localDef.GetNum() == FIT_MESG_NUM_INVALID)
                        {
                            std::ostringstream message;
                            message << "FIT decode error: Missing FIT message definition for local message number " << ((int)localMesgIndex) << ". Error at byte: " << currentByteOffset;
                            throw(RuntimeException(message.str()));
                        }

                        mesg = Mesg(localDef.GetNum());
                        mesg.SetLocalNum(localMesgIndex);

                        if (localDef.GetFields().size() != 0)
                        {
                            state = STATE_FIELD_DATA;
                        }
                        else if (localDef.GetDeveloperFieldTotalSize() > 0)
                        {
                            state = STATE_DEV_FIELD_DATA;
                        }
                        else
                        {
                            return RETURN_MESG;
                        }
                    }
                }
            }
            else
            {
                // We just got the low byte of the crc.
                state = STATE_FILE_CRC_HIGH;
            }
            break;

        case STATE_RESERVED1:
            localMesgDefs[localMesgIndex].ClearFields();
            state = STATE_ARCH;
            break;

        case STATE_ARCH:
            archs[localMesgIndex] = data;
            state = STATE_MESG_NUM_0;
            break;

        case STATE_MESG_NUM_0:
            // Read the global message number bytes in as if they are in little endian format.
            localMesgDefs[localMesgIndex].SetNum((FIT_UINT16)data);
            state = STATE_MESG_NUM_1;
            break;

        case STATE_MESG_NUM_1:
            localMesgDefs[localMesgIndex].SetNum(localMesgDefs[localMesgIndex].GetNum() | ((FIT_UINT16)data << 8));

            // We have to check for endianness.
            if (archs[localMesgIndex] == FIT_ARCH_ENDIAN_BIG) {
                localMesgDefs[localMesgIndex].SetNum((localMesgDefs[localMesgIndex].GetNum() >> 8) | ((localMesgDefs[localMesgIndex].GetNum() & 0xFF) << 8));
            }
            else if (archs[localMesgIndex] != FIT_ARCH_ENDIAN_LITTLE)
            {
                std::ostringstream message;
                message << "FIT decode error: Architecture " << archs[localMesgIndex] << " not supported. Error at byte: " << currentByteOffset;
                throw(RuntimeException(message.str()));
            }

            state = STATE_NUM_FIELDS;
            break;

        case STATE_NUM_FIELDS:
            numFields = data;
            fieldIndex = 0;

            if (numFields == 0)
            {
                if (hasDevData)
                {
                    state = STATE_NUM_DEV_FIELDS;
                }
                else
                {
                    state = STATE_RECORD;
                    return RETURN_MESG_DEF;
                }
            }
            else
            {
                state = STATE_FIELD_NUM;
            }
            break;

        case STATE_FIELD_NUM:
            localMesgDefs[localMesgIndex].AddField(FieldDefinition());
            localMesgDefs[localMesgIndex].GetFieldByIndex(fieldIndex)->SetNum(data);
            state = STATE_FIELD_SIZE;
            break;

        case STATE_FIELD_SIZE:
            if ( data == 0 )
            {
                // Bad Size
                std::ostringstream message;
                message << "FIT decode error: Invalid Field Size " << data << ". Error at byte: " << currentByteOffset;
                throw(RuntimeException(message.str()));
            }

            localMesgDefs[localMesgIndex].GetFieldByIndex(fieldIndex)->SetSize(data);
            state = STATE_FIELD_TYPE;
            break;

        case STATE_FIELD_TYPE:
            localMesgDefs[localMesgIndex].GetFieldByIndex(fieldIndex)->SetType(data);

            if (++fieldIndex >= numFields)
            {
                if (hasDevData)
                {
                    state = STATE_NUM_DEV_FIELDS;
                }
                else
                {
                    state = STATE_RECORD;
                    return RETURN_MESG_DEF;
                }
            }
            else
            {
                state = STATE_FIELD_NUM;
            }
            break;

        case STATE_NUM_DEV_FIELDS:
            numFields = data;
            fieldIndex = 0;

            if (numFields == 0)
            {
                state = STATE_RECORD;
                return RETURN_MESG_DEF;
            }

            state = STATE_DEV_FIELD_NUM;
            break;

        case STATE_DEV_FIELD_NUM:
            fieldData[DevFieldNumOffset] = data;
            state = STATE_DEV_FIELD_SIZE;
            break;

        case STATE_DEV_FIELD_SIZE:
            fieldData[DevFieldSizeOffset] = data;
            state = STATE_DEV_FIELD_INDEX;
            break;

        case STATE_DEV_FIELD_INDEX:
            fieldData[DevFieldIndexOffset] = data;

            try
            {
                const FieldDescriptionMesg& desc = descriptions
                    .at(fieldData[DevFieldIndexOffset])
                    .at(fieldData[DevFieldNumOffset]);
                const DeveloperDataIdMesg& developer = developers
                    .at( fieldData[DevFieldIndexOffset] );

                localMesgDefs[localMesgIndex]
                    .AddDevField(DeveloperFieldDefinition(desc, developer, fieldData[DevFieldSizeOffset]));
            }
            catch (std::out_of_range)
            {
                // No Matching Description Message add a Generic Definition
                localMesgDefs[localMesgIndex]
                    .AddDevField(DeveloperFieldDefinition(
                        fieldData[DevFieldNumOffset],
                        fieldData[DevFieldSizeOffset],
                        fieldData[DevFieldIndexOffset]));
            }

            if (++fieldIndex >= numFields)
            {
                state = STATE_RECORD;
                return RETURN_MESG_DEF;
            }

            state = STATE_DEV_FIELD_NUM;
            break;

        case STATE_FIELD_DATA: {
            MesgDefinition& localDef = localMesgDefs[localMesgIndex];
            size_t numFieldsInDef = localDef.GetFields().size();

            if (fieldBytesLeft == 0)
            {
                fieldDataIndex = 0;
                FieldDefinition* fld = localDef.GetFieldByIndex(fieldIndex);
                fieldBytesLeft = fld->GetSize();

                if (fieldBytesLeft == 0)
                {
                    fieldBytesLeft = localDef.GetFieldByIndex(++fieldIndex)->GetSize();
                }
            }

            fieldData[fieldDataIndex++] = data;
            fieldBytesLeft--;

            if (fieldBytesLeft == 0)
            {
                FieldDefinition* fldDefn = localDef.GetFieldByIndex(fieldIndex);
                FIT_UINT8 baseType = fldDefn->GetType() & FIT_BASE_TYPE_NUM_MASK;
                FIT_UINT8 typeSize = baseTypeSizes[baseType];
                FIT_BOOL read = FIT_TRUE;

                if (baseType < FIT_BASE_TYPES) // Ignore field if base type not supported.
                {
                    UpdateEndianness(fldDefn->GetType(), fldDefn->GetSize());

                    Field field(mesg.GetNum(), fldDefn->GetNum());
                    if (field.IsValid()) // If known field type.
                    {
                        if ( field.GetType() != fldDefn->GetType() )
                        {
                            FIT_UINT8 profileSize = fit::baseTypeSizes[( field.GetType() & FIT_BASE_TYPE_NUM_MASK )];
                            if ( typeSize < profileSize )
                            {
                                field.SetBaseType( fldDefn->GetType() );
                            }
                            else if ( typeSize != profileSize )
                            {
                                // Demotion is hard. Don't read the field if the
                                // sizes are different. Use the profile type if the
                                // signedness of the field has changed.
                                read = FIT_FALSE;
                            }
                        }

                        if ( read )
                        {
                            field.Read(&fieldData, fldDefn->GetSize());
                        }

                        // The special case time record.
                        if (fldDefn->GetNum() == FIT_FIELD_NUM_TIMESTAMP)
                        {
                            timestamp = field.GetUINT32Value();
                            lastTimeOffset = (FIT_UINT8)(timestamp & FIT_HDR_TIME_OFFSET_MASK);
                        }

                        //Allows messages containing the accumulated field to set the accumulated value
                        FIT_UINT16 numValues = field.GetNumValues();
                        if ( field.GetIsAccumulated() )
                        {
                            FIT_UINT16 fieldNum = field.GetNum();
                            FIT_FLOAT64 fieldScale = field.GetScale();
                            FIT_FLOAT64 fieldOffset = field.GetOffset();
                            FIT_UINT16 numMesgFields = mesg.GetNumFields();
                            FIT_UINT8 i;
                            for (i = 0; i < numValues; i++)
                            {
                                FIT_FLOAT64 value = field.GetRawValue(i);
                                FIT_UINT16 j;
                                for (j = 0; j < numMesgFields; j++)
                                {
                                    FIT_UINT16 k;
                                    Field* containingField = mesg.GetFieldByIndex(j);
                                    FIT_UINT16 numComponents = containingField->GetNumComponents();

                                    for (k = 0; k < numComponents; k++)
                                    {
                                        const Profile::FIELD_COMPONENT* fc = containingField->GetComponent(k);
                                        if ( ( fc->num == fieldNum ) && ( fc->accumulate ) )
                                        {
                                            value = ((((value / fieldScale) - fieldOffset) + fc->offset) * fc->scale);
                                        }
                                    }
                                }
                                accumulator.Set(mesg.GetNum(), fieldNum, (FIT_UINT32)value);
                            }
                        }

                        if (numValues > 0)
                        {
                            mesg.AddField(field);
                        }
                    }
                }
                fieldIndex++;
            }

            if (fieldIndex >= numFieldsInDef)
            {
                // Now that the entire message is decoded we may evaluate subfields and expand components
                for (FIT_UINT16 i=0; i<mesg.GetNumFields(); i++)
                {
                    FIT_UINT16 activeSubField = mesg.GetActiveSubFieldIndexByFieldIndex(i);
                    if( !suppressComponentExpansion )
                    {
                        Field* field = mesg.GetFieldByIndex(i);
                        if (activeSubField == FIT_SUBFIELD_INDEX_MAIN_FIELD)
                        {
                            FIT_UINT16 numComponents = field->GetNumComponents();
                            if (numComponents > 0)
                            {
                                ExpandComponents(field, field->GetComponent(0), numComponents);
                            }
                        }
                        else
                        {
                            const Profile::SUBFIELD* subfield = field->GetSubField(activeSubField);
                            if (subfield->numComponents > 0)
                            {
                                ExpandComponents(field, subfield->components, subfield->numComponents);
                            }
                        }
                    }
                }

                if (localDef.GetDeveloperFieldTotalSize() > 0)
                {
                    fieldIndex = 0;
                    fieldBytesLeft = 0;
                    state = STATE_DEV_FIELD_DATA;
                }
                else
                {
                    state = STATE_RECORD;
                    return RETURN_MESG;
                }
            }
            break;
        }

        case STATE_DEV_FIELD_DATA: {
             MesgDefinition& localMesgDef = localMesgDefs[localMesgIndex];
             DeveloperFieldDefinition* fieldDef = localMesgDef.GetDevFieldByIndex(fieldIndex);
             size_t numDevFields = localMesgDef.GetDevFields().size();

             if (fieldBytesLeft == 0)
             {
                 fieldDataIndex = 0;
                 fieldBytesLeft = fieldDef->GetSize();

                 if (fieldBytesLeft == 0)
                 {
                     fieldBytesLeft = localMesgDefs->
                         GetDevFieldByIndex(++fieldIndex)->GetSize();
                 }
             }

            fieldData[fieldDataIndex++] = data;
            fieldBytesLeft--;

             if (fieldBytesLeft == 0)
             {
                 DeveloperFieldDefinition* fldDefn = localMesgDef.GetDevFieldByIndex(fieldIndex);
                 FIT_UINT8 baseType = fldDefn->GetType() & FIT_BASE_TYPE_NUM_MASK;

                 if (baseType < FIT_BASE_TYPES) // Ignore field if base type not supported.
                 {
                     DeveloperField field(*fldDefn);

                     UpdateEndianness(fldDefn->GetType(), fldDefn->GetSize());
                     field.Read(&fieldData, fldDefn->GetSize());
                     mesg.AddDeveloperField(field);
                 }

                 fieldIndex++;

                 if (fieldIndex >= numDevFields) {
                     // Mesg decode complete
                     state = STATE_RECORD;
                     return RETURN_MESG;
                 }
             }
            break;
        }

        default:
            break;
    }

    return RETURN_CONTINUE;
}
