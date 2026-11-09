FIT_BOOL Decode::Resume(void)
{
    pause = FIT_FALSE;
    RETURN decodeReturn = RETURN_CONTINUE;

    do
    {
        if ( currentByteIndex == 0 )
        {
            file->read(buffer, BufferSize);
            bytesRead = (FIT_UINT32)file->gcount();
            if (pause && bytesRead > 0)
                return FIT_FALSE;
        }

        FIT_UINT32 byteIndex = currentByteIndex;
        FIT_UINT32 const end = bytesRead;
        FIT_UINT32 offset = currentByteOffset;

        for (; byteIndex < end; ++byteIndex)
        {
            currentByteIndex = byteIndex;
            decodeReturn = ReadByte((FIT_UINT8)buffer[byteIndex]);

            if (decodeReturn == RETURN_CONTINUE)
            {
                ++offset;
                continue;
            }

            if (decodeReturn == RETURN_MESG)
            {
                FIT_UINT16 mesgNum = mesg.GetNum();

                if (mesgNum == FIT_MESG_NUM_DEVELOPER_DATA_ID)
                {
                    DeveloperDataIdMesg devIdMesg(mesg);

                    if (!devIdMesg.IsDeveloperDataIndexValid()) {
                        throw fit::RuntimeException("Invalid developer data index in DeveloperDataIdMesg");
                    }

                    FIT_UINT8 index = devIdMesg.GetDeveloperDataIndex();
                    developers[index] = devIdMesg;
                    descriptions[index] = std::unordered_map<FIT_UINT8, FieldDescriptionMesg>();
                }
                else if (mesgNum == FIT_MESG_NUM_FIELD_DESCRIPTION)
                {
                    FieldDescriptionMesg descMesg(mesg);

                    if (!descMesg.IsDeveloperDataIndexValid()) {
                        throw fit::RuntimeException("Invalid developer data index in FieldDescriptionMesg");
                    }

                    if (!descMesg.IsFieldDefinitionNumberValid())
                    {
                        throw fit::RuntimeException("Invalid developer field definition number in FieldDescriptionMesg");
                    }

                    FIT_UINT8 index = descMesg.GetDeveloperDataIndex();
                    FIT_UINT8 fldNum = descMesg.GetFieldDefinitionNumber();

                    try
                    {
                        descriptions.at(index)[fldNum] = descMesg;

                        if (descriptionListener)
                        {
                            descriptionListener->OnDeveloperFieldDescription(DeveloperFieldDescription(descMesg, developers[index]));
                        }
                    }
                    catch (std::out_of_range)
                    {
                        // Description without a Developer Data Id Message
                    }
                }

                if (mesgListener)
                    mesgListener->OnMesg(mesg);

                ++offset;
                if (pause)
                {
                    if (byteIndex + 1 < end)
                    {
                        currentByteIndex = byteIndex + 1;
                        currentByteOffset = offset;
                        return FIT_FALSE;
                    }
                    byteIndex = end;
                }
                continue;
            }

            if (decodeReturn == RETURN_MESG_DEF)
            {
                if (mesgDefinitionListener)
                {
                    mesgDefinitionListener->OnMesgDefinition(localMesgDefs[localMesgIndex]);
                }

                ++offset;
                if (pause)
                {
                    if (byteIndex + 1 < end)
                    {
                        currentByteIndex = byteIndex + 1;
                        currentByteOffset = offset;
                        return FIT_FALSE;
                    }
                    byteIndex = end;
                }
                continue;
            }

            if (decodeReturn == RETURN_END_OF_FILE)
            {
                currentByteIndex = byteIndex + 1;
                currentByteOffset = offset + 1;
                return FIT_TRUE;
            }

            currentByteIndex = byteIndex;
            currentByteOffset = offset + 1;
            return FIT_TRUE;
        }

        currentByteOffset = offset;
        currentByteIndex = 0;
    } while ( file->good() );

    if ((streamIsComplete == FIT_TRUE) && (skipHeader == FIT_FALSE))
    {
        std::ostringstream message;
        message << "FIT decode error: Unexpected end of input stream at byte: " << currentByteOffset;
        throw RuntimeException(message.str());
    }
    if (streamIsComplete == FIT_FALSE)
    {
        if ((decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF))
        {
            return FIT_TRUE;
        }
        else
        {
            return FIT_FALSE;
        }
    }
    else
    {
        if ((decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF))
        {
            return FIT_TRUE;
        }
        else
        {
            if (invalidDataSize == FIT_FALSE)
            {
                std::ostringstream message;
                message << "FIT decode error: Unexpected end of input stream at byte: " << currentByteOffset;
                throw RuntimeException(message.str());
            }
            else
            {
                return FIT_TRUE;
            }
        }
    }
}
