<a name="readme-top"></a>
<!-- PROJECT TITLE -->
<div align="center">
<h1 align="center">SFTP REPLICATE WITH AIRFLOW</h1>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#description-of-the-problem">Description of the problem</a>
      <ul>
        <li><a href="#examples">Examples</a></li>
      </ul>
    </li>
    <li>
        <a href="#project-structure">Project Structure</a>
    </li>
  </ol>
</details>

<!-- Description of the problem -->
## Description of the problem  
Develop an Apache Airflow DAG that facilitates the transfer of files from the SFTP server at `<ftp-server>` to the SFTP server at `<ftp-replicate>`
and ensures the preservation of the original directory structure.  
The synchronization process should be unidirectional; hence, any modification made on `<ftp-replicate>` must not impact the `<ftp-server>`.  
Deleted files on SFTP server at <ftp-server> must remain intact on <ftp-replcate> server. But a prefix 'deleted_' is added to the file's name  

### Examples:  
* On March 1st, 2024, when a file named sftp://<ftp-server>/a/b/c/file_1.txt is detected on the source server, it should be replicated to sftp://<ftp-replicate>/a/b/c/file_1.txt on the destination server.  
* On March 2nd, 2024, a file named sftp://<ftp-server>/a/b/c/file_2.txt appears on the source server and subsequently should be transferred to sftp://<ftp-replicate>/a/b/c/file_2.txt on the destination server.  
* On March 3rd, 2024, a file has been renamed to sftp://<ftp-server>/a/b/c/file_3.txt in the source server and the file in sftp://<ftp-replicate>/a/b/c/file_3.txt on the destination server should be renamed.
* On March 4th, 2024, a file has been deleted sftp://<ftp-server>/a/b/c/file_4.txt in the source server and the file in sftp://<ftp-replicate>/a/b/c/deleted_file_4.txt on the destination server should be removed.  

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- Explain solution -->  
## Explain solution  
1. Read file from ftp source  
2. Check if the file has been transferred previously    
- If the file has been transferred in the past, it will be skipped  
- If the file has not been transferred in the past, it will be transferred

<p align="right">(<a href="#readme-top">back to top</a>)</p>
