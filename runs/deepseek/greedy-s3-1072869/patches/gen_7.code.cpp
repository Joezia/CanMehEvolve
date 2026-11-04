FIT_BOOL Decode::Resume(void)
{
    pause = FIT_FALSE;
    RETURN decodeReturn = RETURN_CONTINUE;
    bool checkPause = false;
    FIT_UINT32 offset = currentByteOffset;

    do
    {
        if ( currentByteIndex == 0 )
        {
            file->read(buffer, BufferSize);
            bytesRead = (FIT_UINT32)file->gcount();
        }

        FIT_UINT8* p = buffer + currentByteIndex;
        FIT_UINT8* const end = buffer + bytesRead;
        for (; p < end; ++p)
        {
            if (checkPause)
            {
                if (pause)
                {
                    currentByteIndex = (FIT_UINT32)(p - buffer);
                    currentByteOffset = offset;
                    return FIT_FALSE;
                }
                checkPause = false;
            }

            decodeReturn = ReadByte(*p);

            if (decodeReturn == RETURN_CONTINUE)
            {
                ++offset;
                continue;
            }

            switch (decodeReturn) {
                case RETURN_MESG:
                {
                    currentByteOffset = offset;
                    auto mesgNum = mesg.GetNum();
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

                        auto descIt = descriptions.find(index);
                        if (descIt != descriptions.end())
                        {
                            descIt->second[fldNum] = descMesg;

                            if (descriptionListener)
                            {
                                try
                                {
                                    descriptionListener->OnDeveloperFieldDescription(DeveloperFieldDescription(descMesg, developers[index]));
                                }
                                catch (std::out_of_range)
                                {
                                    // Description without a Developer Data Id Message
                                }
                            }
                        }
                    }

                    if (mesgListener)
                        mesgListener->OnMesg(mesg);
                    checkPause = pause;
                    break;
                }

                case RETURN_MESG_DEF:
                    currentByteOffset = offset;
                    if (mesgDefinitionListener)
                    {
                        mesgDefinitionListener->OnMesgDefinition(localMesgDefs[localMesgIndex]);
                    }
                    checkPause = pause;
                    break;

                case RETURN_END_OF_FILE:
                    currentByteIndex = (FIT_UINT32)(p - buffer) + 1;
                    currentByteOffset = offset + 1;
                    return FIT_TRUE;

                default:
                    currentByteIndex = (FIT_UINT32)(p - buffer);
                    currentByteOffset = offset + 1;
                    return FIT_TRUE;
            }
            ++offset;
        }
        currentByteIndex = 0;
        currentByteOffset = offset;
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
