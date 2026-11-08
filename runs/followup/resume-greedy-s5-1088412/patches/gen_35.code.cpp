FIT_BOOL Decode::Resume(void)
{
    pause = FIT_FALSE;
    RETURN decodeReturn = RETURN_CONTINUE;

    FIT_UINT32 idx = currentByteIndex;
    FIT_UINT32 offset = currentByteOffset;
    FIT_BOOL checkPause = FIT_FALSE;

    do
    {
        if ( idx == 0 )
        {
            file->read(buffer, BufferSize);
            bytesRead = (FIT_UINT32)file->gcount();
        }

        const FIT_UINT8* p = buffer + idx;
        const FIT_UINT8* end = buffer + bytesRead;

        while ( p < end )
        {
            decodeReturn = ReadByte((FIT_UINT8)*p);

            if ( decodeReturn == RETURN_CONTINUE )
            {
                ++p;
                ++offset;
                continue;
            }

            currentByteIndex = (FIT_UINT32)(p - buffer);
            currentByteOffset = offset;

            switch (decodeReturn) {
                case RETURN_MESG:
                {
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

                        try
                        {
                            descriptions.at(index)[fldNum] = descMesg;

                            if (descriptionListener)
                            {
                                checkPause = FIT_TRUE;
                                descriptionListener->OnDeveloperFieldDescription(DeveloperFieldDescription(descMesg, developers[index]));
                            }
                        }
                        catch (std::out_of_range)
                        {
                            // Description without a Developer Data Id Message
                        }
                    }

                    if (mesgListener)
                    {
                        checkPause = FIT_TRUE;
                        mesgListener->OnMesg(mesg);
                    }
                    break;
                }

                case RETURN_MESG_DEF:
                    if (mesgDefinitionListener)
                    {
                        checkPause = FIT_TRUE;
                        mesgDefinitionListener->OnMesgDefinition(localMesgDefs[localMesgIndex]);
                    }
                    break;

                case RETURN_END_OF_FILE:
                    ++p;
                    ++offset;
                    currentByteIndex = (FIT_UINT32)(p - buffer);
                    currentByteOffset = offset;
                    return FIT_TRUE;

                default:
                    ++offset;
                    currentByteIndex = (FIT_UINT32)(p - buffer);
                    currentByteOffset = offset;
                    return FIT_TRUE;
            }

            ++p;
            ++offset;

            if ( checkPause )
            {
                checkPause = FIT_FALSE;
                if ( pause )
                {
                    currentByteIndex = (FIT_UINT32)(p - buffer);
                    currentByteOffset = offset;
                    return FIT_FALSE;
                }
            }
        }

        currentByteIndex = 0;
        idx = 0;
        currentByteOffset = offset;
    } while ( file->good() );

    if ((streamIsComplete == FIT_TRUE) && (skipHeader == FIT_FALSE))
    {
        // When decoding a complete file we should exit via RETURN_END_OF_FILE state only.
        std::ostringstream message;
        message << "FIT decode error: Unexpected end of input stream at byte: " << currentByteOffset;
        throw RuntimeException(message.str());
    }
    if (streamIsComplete == FIT_FALSE)
    {
        // If stream is not yet complete caller can resume() when there is more data
        // or decide there was an error.
        if ((decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF))
        {
            // Our stream ended on a complete message, maybe we are done decoding.
            return FIT_TRUE;
        }
        else
        {
            // EOF was encountered mid message. Caller may want to resume once
            // more bytes are available.
            return FIT_FALSE;
        }
    }
    else
    {
        if ((decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF))
        {
            // Our stream ended on a complete message, we are done decoding.
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
