FIT_BOOL Decode::Resume(void)
{
    pause = FIT_FALSE;
    RETURN decodeReturn = RETURN_CONTINUE;
    FIT_BOOL checkPause = FIT_FALSE;

    do
    {
        if ( currentByteIndex == 0 )
        {
            file->read(buffer, BufferSize);
            bytesRead = (FIT_UINT32)file->gcount();
        }

        FIT_UINT32 i = currentByteIndex;
        const FIT_UINT32 n = bytesRead;
        FIT_UINT32 off = currentByteOffset;
        const FIT_UINT8* buf = reinterpret_cast<const FIT_UINT8*>(buffer);

        for (; i < n; ++i)
        {
            if (checkPause)
            {
                if (pause)
                {
                    currentByteIndex = i;
                    currentByteOffset = off;
                    return FIT_FALSE;
                }
                checkPause = FIT_FALSE;
            }

            currentByteIndex = i;
            currentByteOffset = off;
            decodeReturn = ReadByte(buf[i]);

            if (decodeReturn == RETURN_CONTINUE)
            {
                ++off;
                continue;
            }

            switch (decodeReturn) {
                case RETURN_MESG:
                {
                    const auto num = mesg.GetNum();
                    if (num == FIT_MESG_NUM_DEVELOPER_DATA_ID)
                    {
                        DeveloperDataIdMesg devIdMesg(mesg);

                        if (!devIdMesg.IsDeveloperDataIndexValid()) {
                            throw fit::RuntimeException("Invalid developer data index in DeveloperDataIdMesg");
                        }

                        FIT_UINT8 index = devIdMesg.GetDeveloperDataIndex();
                        developers[index] = devIdMesg;
                        descriptions[index] = std::unordered_map<FIT_UINT8, FieldDescriptionMesg>();
                    }
                    else if (num == FIT_MESG_NUM_FIELD_DESCRIPTION)
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

                    ++off;
                    checkPause = FIT_TRUE;
                    break;
                }

                case RETURN_MESG_DEF:
                    if (mesgDefinitionListener)
                    {
                        mesgDefinitionListener->OnMesgDefinition(localMesgDefs[localMesgIndex]);
                    }
                    ++off;
                    checkPause = FIT_TRUE;
                    break;

                case RETURN_END_OF_FILE:
                    ++i;
                    ++off;
                    currentByteIndex = i;
                    currentByteOffset = off;
                    return FIT_TRUE;

                default:
                    ++off;
                    currentByteIndex = i;
                    currentByteOffset = off;
                    return FIT_TRUE;
            }
        }
        currentByteIndex = 0;
        currentByteOffset = off;
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
