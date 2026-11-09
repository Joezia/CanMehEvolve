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
        }

        const auto* buf = buffer;
        auto idx = currentByteIndex;
        const auto n = bytesRead;
        auto offset = currentByteOffset;

        for (; idx < n; ++idx)
        {
            if (pause)
            {
                currentByteIndex = idx;
                currentByteOffset = offset;
                return FIT_FALSE;
            }

            decodeReturn = ReadByte((FIT_UINT8)buf[idx]);

            if (decodeReturn == RETURN_CONTINUE)
            {
                ++offset;
                continue;
            }

            if (decodeReturn == RETURN_MESG)
            {
                currentByteIndex = idx;
                currentByteOffset = offset;

                const auto mesgNum = mesg.GetNum();
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
            }
            else if (decodeReturn == RETURN_MESG_DEF)
            {
                currentByteIndex = idx;
                currentByteOffset = offset;

                if (mesgDefinitionListener)
                {
                    mesgDefinitionListener->OnMesgDefinition(localMesgDefs[localMesgIndex]);
                }
            }
            else if (decodeReturn == RETURN_END_OF_FILE)
            {
                currentByteIndex = idx + 1;
                currentByteOffset = offset + 1;
                return FIT_TRUE;
            }
            else
            {
                currentByteIndex = idx;
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
        // if Decoding Records section only, file should end on a complete message
        // (unless incomplete stream option above was also used)
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
